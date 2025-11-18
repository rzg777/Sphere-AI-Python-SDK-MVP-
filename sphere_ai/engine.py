"""Policy engine for evaluating security rules against LLM interactions."""

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .exceptions import SpherePolicyError


class RuleAction(str, Enum):
    """Available actions for security rules."""
    BLOCK = "block"
    REDACT = "redact"
    ALLOW = "allow"
    LOG = "log"


class RuleType(str, Enum):
    """Types of security rules."""
    TOOL_FILTER = "tool_filter"
    REGEX_MASK = "regex_mask"
    CONTENT_FILTER = "content_filter"


@dataclass
class Violation:
    """Represents a policy violation."""
    rule_id: str
    trigger: str
    type: str
    compliance_tag: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationResult:
    """Result of policy evaluation."""
    blocked: bool = False
    violations: List[Violation] = field(default_factory=list)
    modified_messages: Optional[List[Dict[str, Any]]] = None


@dataclass
class BaseRule:
    """Base class for all security rules."""

    id: str
    type: RuleType
    action: RuleAction
    compliance_tag: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            self.type = RuleType(self.type)
        if isinstance(self.action, str):
            self.action = RuleAction(self.action)


@dataclass
class ToolFilterRule(BaseRule):
    """Rule for filtering tool/function calls."""

    blocked_tools: List[str] = field(default_factory=list)
    allowed_tools: Optional[List[str]] = None


@dataclass
class RegexMaskRule(BaseRule):
    """Rule for masking sensitive patterns using regex."""

    pattern: str = ""
    replacement: str = "[REDACTED]"
    flags: int = 0


@dataclass
class ContentFilterRule(BaseRule):
    """Rule for content-based filtering."""

    blocked_patterns: List[str] = field(default_factory=list)
    severity_threshold: Optional[str] = None


@dataclass
class PolicyConfig:
    """Configuration for the policy engine."""

    version: str = "1.0"
    compliance_standard: Optional[str] = None
    security_rules: List[Dict[str, Any]] = field(default_factory=list)


class PolicyEngine:
    """
    Engine for evaluating security policies against LLM interactions.
    
    This engine applies rules in sequence and can block requests, redact content,
    or log violations based on the configured policies.
    """
    
    def __init__(self, config: Optional[PolicyConfig] = None, rules: Optional[List[BaseRule]] = None):
        """
        Initialize policy engine.
        
        Args:
            config: Policy configuration from YAML
            rules: List of rule objects
        """
        self.rules: List[BaseRule] = []
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        
        # Load rules from configuration
        if config:
            self._load_rules_from_config(config)
        
        # Add direct rules
        if rules:
            self.rules.extend(rules)
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _load_rules_from_config(self, config: PolicyConfig) -> None:
        """Load rules from YAML configuration."""
        for rule_data in config.security_rules:
            rule_type = rule_data.get("type")
            
            try:
                if rule_type == RuleType.TOOL_FILTER:
                    rule = ToolFilterRule(**rule_data)
                elif rule_type == RuleType.REGEX_MASK:
                    rule = RegexMaskRule(**rule_data)
                elif rule_type == RuleType.CONTENT_FILTER:
                    rule = ContentFilterRule(**rule_data)
                else:
                    raise SpherePolicyError(f"Unknown rule type: {rule_type}")
                
                self.rules.append(rule)
                
            except Exception as e:
                raise SpherePolicyError(f"Failed to load rule {rule_data.get('id')}: {e}")
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance."""
        for rule in self.rules:
            if isinstance(rule, RegexMaskRule):
                try:
                    self.compiled_patterns[rule.id] = re.compile(rule.pattern, rule.flags)
                except re.error as e:
                    raise SpherePolicyError(f"Invalid regex pattern in rule {rule.id}: {e}")
    
    def evaluate_pre_flight(self, context: Any) -> EvaluationResult:
        """
        Evaluate policies before sending request to LLM.
        
        Args:
            context: Interaction context with messages and tools
            
        Returns:
            EvaluationResult: Result of pre-flight evaluation
        """
        result = EvaluationResult()
        modified_messages = context.messages.copy() if context.messages else []
        
        for rule in self.rules:
            rule_result = self._evaluate_rule_pre_flight(rule, context, modified_messages)

            if rule_result.violations:
                result.violations.extend(rule_result.violations)

            if rule_result.blocked:
                result.blocked = True
                # Early termination for blocking rules
                if rule.action == RuleAction.BLOCK:
                    return result
            
            if rule_result.modified_messages:
                modified_messages = rule_result.modified_messages
        
        if modified_messages != context.messages:
            result.modified_messages = modified_messages
        
        return result
    
    def evaluate_post_flight(self, context: Any, response: Any) -> EvaluationResult:
        """
        Evaluate policies after receiving response from LLM.
        
        Args:
            context: Interaction context
            response: LLM response object
            
        Returns:
            EvaluationResult: Result of post-flight evaluation
        """
        result = EvaluationResult()
        
        for rule in self.rules:
            rule_result = self._evaluate_rule_post_flight(rule, context, response)

            if rule_result.violations:
                result.violations.extend(rule_result.violations)

            if rule_result.blocked:
                result.blocked = True
                # Early termination for blocking rules
                if rule.action == RuleAction.BLOCK:
                    return result
        
        return result
    
    def _evaluate_rule_pre_flight(
        self, 
        rule: BaseRule, 
        context: Any, 
        messages: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate a single rule in pre-flight phase."""
        result = EvaluationResult()
        
        if isinstance(rule, ToolFilterRule):
            return self._evaluate_tool_filter_pre_flight(rule, context)
        elif isinstance(rule, RegexMaskRule):
            return self._evaluate_regex_mask_pre_flight(rule, messages)
        elif isinstance(rule, ContentFilterRule):
            return self._evaluate_content_filter_pre_flight(rule, messages)
        
        return result
    
    def _evaluate_rule_post_flight(
        self, 
        rule: BaseRule, 
        context: Any, 
        response: Any
    ) -> EvaluationResult:
        """Evaluate a single rule in post-flight phase."""
        result = EvaluationResult()
        
        if isinstance(rule, ToolFilterRule):
            return self._evaluate_tool_filter_post_flight(rule, response)
        elif isinstance(rule, RegexMaskRule):
            return self._evaluate_regex_mask_post_flight(rule, response)
        elif isinstance(rule, ContentFilterRule):
            return self._evaluate_content_filter_post_flight(rule, response)
        
        return result
    
    def _evaluate_tool_filter_pre_flight(
        self, 
        rule: ToolFilterRule, 
        context: Any
    ) -> EvaluationResult:
        """Evaluate tool filter rule in pre-flight."""
        result = EvaluationResult()
        
        if not context.tools:
            return result
        
        for tool in context.tools:
            if tool.get("type") == "function":
                function_name = tool["function"].get("name")
                
                # Check if tool is blocked
                if function_name in rule.blocked_tools:
                    violation = Violation(
                        rule_id=rule.id,
                        trigger=function_name,
                        type="tool_call",
                        compliance_tag=rule.compliance_tag,
                        details={"phase": "pre_flight"}
                    )
                    result.violations.append(violation)
                    
                    if rule.action == RuleAction.BLOCK:
                        result.blocked = True
                        return result
        
        return result
    
    def _evaluate_tool_filter_post_flight(
        self, 
        rule: ToolFilterRule, 
        response: Any
    ) -> EvaluationResult:
        """Evaluate tool filter rule in post-flight."""
        result = EvaluationResult()
        
        if not hasattr(response, 'choices') or not response.choices:
            return result
        
        message = response.choices[0].message
        if not message.tool_calls:
            return result
        
        for tool_call in message.tool_calls:
            if tool_call.type == "function":
                function_name = tool_call.function.name
                
                # Check if tool is blocked
                if function_name in rule.blocked_tools:
                    violation = Violation(
                        rule_id=rule.id,
                        trigger=function_name,
                        type="tool_call",
                        compliance_tag=rule.compliance_tag,
                        details={"phase": "post_flight"}
                    )
                    result.violations.append(violation)
                    
                    if rule.action == RuleAction.BLOCK:
                        result.blocked = True
                        return result
        
        return result
    
    def _evaluate_regex_mask_pre_flight(
        self, 
        rule: RegexMaskRule, 
        messages: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate regex mask rule in pre-flight."""
        result = EvaluationResult()
        pattern = self.compiled_patterns.get(rule.id)
        
        if not pattern:
            return result
        
        modified = False
        modified_messages = messages.copy()
        
        for i, message in enumerate(modified_messages):
            if "content" in message and message["content"]:
                original_content = message["content"]
                masked_content = pattern.sub(rule.replacement, original_content)
                
                if masked_content != original_content:
                    modified_messages[i] = {**message, "content": masked_content}
                    modified = True
                    
                    violation = Violation(
                        rule_id=rule.id,
                        trigger=rule.pattern,
                        type="regex_mask",
                        compliance_tag=rule.compliance_tag,
                        details={
                            "phase": "pre_flight",
                            "redacted_content": True
                        }
                    )
                    result.violations.append(violation)
        
        if modified:
            result.modified_messages = modified_messages
        
        return result
    
    def _evaluate_regex_mask_post_flight(
        self, 
        rule: RegexMaskRule, 
        response: Any
    ) -> EvaluationResult:
        """Evaluate regex mask rule in post-flight."""
        # Note: Post-flight regex masking would require modifying the response
        # For now, we just log violations without modifying
        result = EvaluationResult()
        pattern = self.compiled_patterns.get(rule.id)
        
        if not pattern:
            return result
        
        if not hasattr(response, 'choices') or not response.choices:
            return result
        
        message = response.choices[0].message
        if message.content and pattern.search(message.content):
            violation = Violation(
                rule_id=rule.id,
                trigger=rule.pattern,
                type="regex_mask",
                compliance_tag=rule.compliance_tag,
                details={"phase": "post_flight"}
            )
            result.violations.append(violation)
        
        return result
    
    def _evaluate_content_filter_pre_flight(
        self, 
        rule: ContentFilterRule, 
        messages: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Evaluate content filter rule in pre-flight."""
        result = EvaluationResult()
        
        for message in messages:
            if "content" in message and message["content"]:
                content = message["content"].lower()
                
                for pattern in rule.blocked_patterns:
                    if pattern.lower() in content:
                        violation = Violation(
                            rule_id=rule.id,
                            trigger=pattern,
                            type="content_filter",
                            compliance_tag=rule.compliance_tag,
                            details={"phase": "pre_flight"}
                        )
                        result.violations.append(violation)
                        
                        if rule.action == RuleAction.BLOCK:
                            result.blocked = True
                            return result
        
        return result
    
    def _evaluate_content_filter_post_flight(
        self, 
        rule: ContentFilterRule, 
        response: Any
    ) -> EvaluationResult:
        """Evaluate content filter rule in post-flight."""
        result = EvaluationResult()
        
        if not hasattr(response, 'choices') or not response.choices:
            return result
        
        message = response.choices[0].message
        if message.content:
            content = message.content.lower()
            
            for pattern in rule.blocked_patterns:
                if pattern.lower() in content:
                    violation = Violation(
                        rule_id=rule.id,
                        trigger=pattern,
                        type="content_filter",
                        compliance_tag=rule.compliance_tag,
                        details={"phase": "post_flight"}
                    )
                    result.violations.append(violation)
                    
                    if rule.action == RuleAction.BLOCK:
                        result.blocked = True
                        return result
        
        return result
