"""Structured NDJSON audit logging for compliance and governance."""

import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class AuditLogEntry:
    """Base structure for audit log entries."""
    timestamp: str
    level: str
    source: str = "sphere_sdk"
    interaction_id: Optional[str] = None
    model: Optional[str] = None
    policy_decision: Optional[str] = None
    violation: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None
    cost_metric: Optional[Dict[str, Any]] = None
    phase: Optional[str] = None
    error: Optional[str] = None


class AuditLogger:
    """
    NDJSON audit logger for compliance and governance.
    
    Emits structured JSON logs to stdout for easy integration with
    logging pipelines and compliance monitoring systems.
    """
    
    def __init__(self, enabled: bool = True, output_stream=sys.stdout):
        """
        Initialize audit logger.
        
        Args:
            enabled: Whether logging is enabled
            output_stream: Output stream for logs (default: stdout)
        """
        self.enabled = enabled
        self.output_stream = output_stream
    
    def _emit_log(self, log_data: Dict[str, Any]) -> None:
        """Emit a single NDJSON log entry."""
        if not self.enabled:
            return
        
        try:
            json_line = json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))
            print(json_line, file=self.output_stream, flush=True)
        except Exception as e:
            # Fallback to prevent logging failures from breaking the application
            error_log = {
                "timestamp": self._current_timestamp(),
                "level": "ERROR",
                "source": "sphere_sdk",
                "error": f"Failed to emit audit log: {e}",
                "original_data": str(log_data)[:200]  # Truncate for safety
            }
            print(json.dumps(error_log), file=sys.stderr, flush=True)
    
    def _current_timestamp(self) -> str:
        """Get current timestamp in ISO format with timezone."""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def log_violation(
        self,
        interaction_id: str,
        model: str,
        policy_decision: str,
        violation: Any,
        cost_metric: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a policy violation.
        
        Args:
            interaction_id: Unique identifier for the interaction
            model: LLM model used
            policy_decision: Decision made (BLOCKED, ALLOWED, etc.)
            violation: Violation details
            cost_metric: Token usage and cost metrics
        """
        log_entry = AuditLogEntry(
            timestamp=self._current_timestamp(),
            level="AUDIT",
            interaction_id=interaction_id,
            model=model,
            policy_decision=policy_decision,
            violation={
                "rule_id": violation.rule_id,
                "trigger": violation.trigger,
                "type": violation.type,
            },
            compliance={
                "standard": "ISO_42001",  # Default, can be overridden per rule
                "control_id": violation.compliance_tag,
            } if violation.compliance_tag else None,
            cost_metric=cost_metric or {},
        )
        
        self._emit_log(self._to_dict(log_entry))
    
    def log_success(
        self,
        interaction_id: str,
        model: str,
        cost_metric: Dict[str, Any],
    ) -> None:
        """
        Log a successful interaction.
        
        Args:
            interaction_id: Unique identifier for the interaction
            model: LLM model used
            cost_metric: Token usage and cost metrics
        """
        log_entry = AuditLogEntry(
            timestamp=self._current_timestamp(),
            level="AUDIT",
            interaction_id=interaction_id,
            model=model,
            policy_decision="ALLOWED",
            cost_metric=cost_metric,
        )
        
        self._emit_log(self._to_dict(log_entry))
    
    def log_error(
        self,
        interaction_id: str,
        model: str,
        phase: str,
        error: str,
    ) -> None:
        """
        Log an error during processing.
        
        Args:
            interaction_id: Unique identifier for the interaction
            model: LLM model used
            phase: Processing phase where error occurred
            error: Error message
        """
        log_entry = AuditLogEntry(
            timestamp=self._current_timestamp(),
            level="ERROR",
            interaction_id=interaction_id,
            model=model,
            phase=phase,
            error=error,
        )
        
        self._emit_log(self._to_dict(log_entry))
    
    def _to_dict(self, entry: AuditLogEntry) -> Dict[str, Any]:
        """Convert AuditLogEntry to dictionaryI'll continue with the complete implementation of the Sphere AI SDK. Let me finish the remaining files:

<dyad-write path="sphere_ai/logging.py" description="NDJSON audit logging system">
"""Structured NDJSON audit logging for compliance and governance."""

import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class AuditLogEntry:
    """Base structure for audit log entries."""
    timestamp: str
    level: str
    source: str = "sphere_sdk"
    interaction_id: Optional[str] = None
    model: Optional[str] = None
    policy_decision: Optional[str] = None
    violation: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None
    cost_metric: Optional[Dict[str, Any]] = None
    phase: Optional[str] = None
    error: Optional[str] = None


class AuditLogger:
    """
    NDJSON audit logger for compliance and governance.
    
    Emits structured JSON logs to stdout for easy integration with
    logging pipelines and compliance monitoring systems.
    """
    
    def __init__(self, enabled: bool = True, output_stream=sys.stdout):
        """
        Initialize audit logger.
        
        Args:
            enabled: Whether logging is enabled
            output_stream: Output stream for logs (default: stdout)
        """
        self.enabled = enabled
        self.output_stream = output_stream
    
    def _emit_log(self, log_data: Dict[str, Any]) -> None:
        """Emit a single NDJSON log entry."""
        if not self.enabled:
            return
        
        try:
            json_line = json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))
            print(json_line, file=self.output_stream, flush=True)
        except Exception as e:
            # Fallback to prevent logging failures from breaking the application
            error_log = {
                "timestamp": self._current_timestamp(),
                "level": "ERROR",
                "source": "sphere_sdk",
                "error": f"Failed to emit audit log: {e}",
                "original_data": str(log_data)[:200]  # Truncate for safety
            }
            print(json.dumps(error_log), file=sys.stderr, flush=True)
    
    def _current_timestamp(self) -> str:
        """Get current timestamp in ISO format with timezone."""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def log_violation(
        self,
        interaction_id: str,
        model: str,
        policy_decision: str,
        violation: Any,
        cost_metric: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a policy violation.
        
        Args:
            interaction_id: Unique identifier for the interaction
            model: LLM model used
            policy_decision: Decision made (BLOCKED, ALLOWED, etc.)
            violation: Violation details
            cost_metric: Token usage and cost metrics
        """
        log_entry = AuditLogEntry(
            timestamp=self._current_timestamp(),
            level="AUDIT",
            interaction_id=interaction_id,
            model=model,
            policy_decision=policy_decision,
            violation={
                "rule_id": violation.rule_id,
                "trigger": violation.trigger,
                "type": violation.type,
            },
            compliance={
                "standard": "ISO_42001",  # Default, can be overridden per rule
                "control_id": violation.compliance_tag,
            } if violation.compliance_tag else None,
            cost_metric=cost_metric or {},
        )
        
        self._emit_log(self._to_dict(log_entry))
    
    def log_success(
        self,
        interaction_id: str,
        model: str,
        cost_metric: Dict[str, Any],
    ) -> None:
        """
        Log a successful interaction.
        
        Args:
            interaction_id: Unique identifier for the interaction
            model: LLM model used
            cost_metric: Token usage and cost metrics
        """
        log_entry = AuditLogEntry(
            timestamp=self._current_timestamp(),
            level="AUDIT",
            interaction_id=interaction_id,
            model=model,
            policy_decision="ALLOWED",
            cost_metric=cost_metric,
        )
        
        self._emit_log(self._to_dict(log_entry))
    
    def log_error(
        self,
        interaction_id: str,
        model: str,
        phase: str,
        error: str,
    ) -> None:
        """
        Log an error during processing.
        
        Args:
            interaction_id: Unique identifier for the interaction
            model: LLM model used
            phase: Processing phase where error occurred
            error: Error message
        """
        log_entry = AuditLogEntry(
            timestamp=self._current_timestamp(),
            level="ERROR",
            interaction_id=interaction_id,
            model=model,
            phase=phase,
            error=error,
        )
        
        self._emit_log(self._to_dict(log_entry))
    
    def _to_dict(self, entry: AuditLogEntry) -> Dict[str, Any]:
        """Convert AuditLogEntry to dictionary."""
        result = {}
        for field, value in entry.__dict__.items():
            if value is not None:
                result[field] = value
        return result