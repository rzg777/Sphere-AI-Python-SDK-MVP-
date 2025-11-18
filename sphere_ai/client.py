"""SphereClient - Drop-in wrapper for OpenAI client with security policies."""

import uuid
import time
from collections.abc import Iterable
from typing import Any, Dict, List, Optional, Union, cast
from dataclasses import dataclass

from .engine import PolicyEngine, PolicyConfig
from .logging import AuditLogger
from .exceptions import SphereSecurityViolation

try:  # Optional dependency: OpenAI SDK
    from openai import OpenAI
    from openai.types.chat import ChatCompletion, ChatCompletionMessage
except ModuleNotFoundError as exc:  # pragma: no cover - triggered in minimal test envs
    OpenAI = None  # type: ignore[assignment]
    ChatCompletion = Any  # type: ignore[assignment]
    ChatCompletionMessage = Any  # type: ignore[assignment]
    _openai_import_error = exc
else:  # pragma: no cover - not triggered in CI
    _openai_import_error = None

try:  # Optional dependency: PyYAML
    from .config import load_config_from_yaml, merge_policies
except ModuleNotFoundError as exc:  # pragma: no cover - triggered in minimal test envs
    load_config_from_yaml = None  # type: ignore[assignment]
    merge_policies = None  # type: ignore[assignment]
    _config_import_error = exc
else:  # pragma: no cover - not triggered in CI
    _config_import_error = None


@dataclass
class InteractionContext:
    """Context for a single LLM interaction."""
    interaction_id: str
    model: str
    start_time: float
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None


class SphereClient:
    """
    Drop-in wrapper for OpenAI client that adds security policies and audit logging.
    
    This class intercepts chat completion requests to apply security policies
    and emit structured audit logs while maintaining full compatibility with
    the OpenAI client interface.
    """
    
    def __init__(
        self,
        openai_client: OpenAI,
        policies: Optional[List[Any]] = None,
        config_path: Optional[str] = "sphere.yaml",
        config: Optional[PolicyConfig] = None,
        policy_engine: Optional[PolicyEngine] = None,
        enable_audit_logging: bool = True,
    ):
        """
        Initialize SphereClient wrapper.
        
        Args:
            openai_client: The OpenAI client instance to wrap
            policies: List of policy packs to apply
            config_path: Path to sphere.yaml configuration file
            config: Programmatic policy configuration
            policy_engine: Pre-configured policy engine (overrides config)
            enable_audit_logging: Whether to emit audit logs to stdout
        """
        if OpenAI is None:
            raise ModuleNotFoundError(
                "SphereClient requires the optional 'openai' dependency. Install the OpenAI "
                "Python package to use SphereClient."
            ) from _openai_import_error
        if load_config_from_yaml is None or merge_policies is None:
            raise ModuleNotFoundError(
                "SphereClient requires the optional 'pyyaml' dependency. Install PyYAML to load "
                "or merge Sphere policy configurations."
            ) from _config_import_error

        self._openai_client = openai_client
        
        # Initialize policy engine
        if policy_engine is not None:
            self.policy_engine = policy_engine
        else:
            # Load configuration from file or use provided config
            file_config = None
            if config_path:
                try:
                    file_config = load_config_from_yaml(config_path)
                except FileNotFoundError:
                    # Config file is optional
                    pass
            
            # Merge file config with programmatic config
            final_config = merge_policies(file_config, config)
            
            # Add policy packs
            additional_rules = []
            policy_packs = policies or []
            for pack in policy_packs:
                if hasattr(pack, 'get_rules'):
                    pack_rules = pack.get_rules()
                    if isinstance(pack_rules, list):
                        additional_rules.extend(pack_rules)

            self.policy_engine = PolicyEngine(
                config=final_config,
                rules=additional_rules if additional_rules else None,
            )
        
        # Initialize audit logger
        self.audit_logger = AuditLogger(enabled=enable_audit_logging)
        
        # Store the original chat.completions for delegation
        self._original_chat_completions = self._openai_client.chat.completions
    
    @property
    def chat(self):
        """Provide access to chat completions with interception."""
        return self
    
    @property 
    def completions(self):
        """Provide access to completions with interception."""
        return self
    
    def create(self, **kwargs) -> ChatCompletion:
        """
        Intercept chat completion creation to apply security policies.
        
        This method:
        1. Creates interaction context
        2. Applies pre-flight policies to input
        3. Delegates to OpenAI API
        4. Applies post-flight policies to output
        5. Emits audit logs
        
        Args:
            **kwargs: Arguments for chat.completions.create
            
        Returns:
            ChatCompletion: The completion response
            
        Raises:
            SphereSecurityViolation: If policies block the request
        """
        # Extract key parameters
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])
        tools = kwargs.get("tools")
        tool_choice = kwargs.get("tool_choice")
        
        # Create interaction context
        interaction_id = f"req_{uuid.uuid4().hex[:8]}"
        context = InteractionContext(
            interaction_id=interaction_id,
            model=model,
            start_time=time.time(),
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        
        # Pre-flight policy evaluation
        try:
            pre_flight_result = self.policy_engine.evaluate_pre_flight(context)
            if pre_flight_result.blocked:
                self._log_violation(context, pre_flight_result, None)
                raise SphereSecurityViolation(
                    f"Request blocked by policy: {pre_flight_result.violations}"
                )
            
            # Apply any modifications from pre-flight
            if pre_flight_result.modified_messages:
                kwargs["messages"] = pre_flight_result.modified_messages
            
        except Exception as e:
            self._log_error(context, "pre_flight_evaluation", str(e))
            raise
        
        # Delegate to OpenAI API
        try:
            start_time = time.time()
            response = self._original_chat_completions.create(**kwargs)
            end_time = time.time()
            
            # Calculate request duration
            duration_ms = int((end_time - start_time) * 1000)
            
        except Exception as e:
            self._log_error(context, "openai_api_call", str(e))
            raise
        
        # Post-flight policy evaluation
        try:
            post_flight_result = self.policy_engine.evaluate_post_flight(context, response)
            if post_flight_result.blocked:
                self._log_violation(context, post_flight_result, response.usage)
                raise SphereSecurityViolation(
                    f"Response blocked by policy: {post_flight_result.violations}"
                )
            
        except Exception as e:
            self._log_error(context, "post_flight_evaluation", str(e))
            # Don't raise here to preserve original response
        
        # Emit audit log
        self._log_success(context, response.usage, duration_ms)
        
        return response
    
    def _log_violation(
        self, 
        context: InteractionContext, 
        result: Any, 
        usage: Optional[Any]
    ) -> None:
        """Log policy violation."""
        cost_metric = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
        }
        
        violations = getattr(result, "violations", [])
        if not violations:
            return

        if isinstance(violations, Iterable) and not isinstance(violations, (str, bytes)):
            violation_iterable = violations
        else:
            violation_iterable = [violations]

        for violation in violation_iterable:
            if not hasattr(violation, "rule_id"):
                continue

            self.audit_logger.log_violation(
                interaction_id=context.interaction_id,
                model=context.model,
                policy_decision="BLOCKED",
                violation=violation,
                cost_metric=cost_metric,
            )
    
    def _log_success(
        self, 
        context: InteractionContext, 
        usage: Optional[Any],
        duration_ms: int
    ) -> None:
        """Log successful interaction."""
        cost_metric = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "duration_ms": duration_ms,
        }
        
        self.audit_logger.log_success(
            interaction_id=context.interaction_id,
            model=context.model,
            cost_metric=cost_metric,
        )
    
    def _log_error(
        self, 
        context: InteractionContext, 
        phase: str, 
        error: str
    ) -> None:
        """Log error during processing."""
        self.audit_logger.log_error(
            interaction_id=context.interaction_id,
            model=context.model,
            phase=phase,
            error=error,
        )
    
    # Delegate other attributes to the wrapped client
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped OpenAI client."""
        return getattr(self._openai_client, name)