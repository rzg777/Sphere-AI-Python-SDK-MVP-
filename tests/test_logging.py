"""Unit tests for NDJSON audit logging."""

import json
import sys
from io import StringIO
from unittest.mock import patch

from sphere_ai.logging import AuditLogger
from sphere_ai.engine import Violation


class TestAuditLogger:
    """Test NDJSON audit logging functionality."""
    
    def test_audit_logger_initialization(self):
        """Test AuditLogger can be initialized."""
        logger = AuditLogger(enabled=True)
        assert logger.enabled is True
        assert logger.output_stream == sys.stdout
        
        custom_stream = StringIO()
        logger = AuditLogger(enabled=False, output_stream=custom_stream)
        assert logger.enabled is False
        assert logger.output_stream == custom_stream
    
    def test_log_violation(self):
        """Test logging policy violations."""
        output_stream = StringIO()
        logger = AuditLogger(enabled=True, output_stream=output_stream)
        
        violation = Violation(
            rule_id="block_destructive_tools",
            trigger="delete_user",
            type="tool_call",
            compliance_tag="ISO_42001_A.9.4"
        )
        
        cost_metric = {
            "prompt_tokens": 50,
            "completion_tokens": 10
        }
        
        logger.log_violation(
            interaction_id="req_123abc",
            model="gpt-4",
            policy_decision="BLOCKED",
            violation=violation,
            cost_metric=cost_metric
        )
        
        log_output = output_stream.getvalue().strip()
        assert log_output
        
        log_data = json.loads(log_output)
        assert log_data["level"] == "AUDIT"
        assert log_data["policy_decision"] == "BLOCKED"
        assert log_data["interaction_id"] == "req_123abc"
        assert log_data["model"] == "gpt-4"
        assert log_data["violation"]["rule_id"] == "block_destructive_tools"
        assert log_data["violation"]["trigger"] == "delete_user"
        assert log_data["compliance"]["control_id"] == "ISO_42001_A.9.4"
        assert log_data["cost_metric"]["prompt_tokens"] == 50
    
    def test_log_success(self):
        """Test logging successful interactions."""
        output_stream = StringIO()
        logger = AuditLogger(enabled=True, output_stream=output_stream)
        
        cost_metric = {
            "prompt_tokens": 100,
            "completion_tokens": 25,
            "duration_ms": 150
        }
        
        logger.log_success(
            interaction_id="req_456def",
            model="gpt-3.5-turbo",
            cost_metric=cost_metric
        )
        
        log_output = output_stream.getvalue().strip()
        assert log_output
        
        log_data = json.loads(log_output)
        assert log_data["level"] == "AUDIT"
        assert log_data["policy_decision"] == "ALLOWED"
        assert log_data["interaction_id"] == "req_456def"
        assert log_data["model"] == "gpt-3.5-turbo"
        assert log_data["cost_metric"]["prompt_tokens"] == 100
        assert log_data["cost_metric"]["duration_ms"] == 150
    
    def test_log_error(self):
        """Test logging errors during processing."""
        output_stream = StringIO()
        logger = AuditLogger(enabled=True, output_stream=output_stream)
        
        logger.log_error(
            interaction_id="req_789ghi",
            model="gpt-4",
            phase="pre_flight_evaluation",
            error="Policy evaluation failed"
        )
        
        log_output = output_stream.getvalue().strip()
        assert log_output
        
        log_data = json.loads(log_output)
        assert log_data["level"] == "ERROR"
        assert log_data["interaction_id"] == "req_789ghi"
        assert log_data["phase"] == "pre_flight_evaluation"
        assert log_data["error"] == "Policy evaluation failed"
    
    def test_logging_disabled(self):
        """Test that logging is disabled when enabled=False."""
        output_stream = StringIO()
        logger = AuditLogger(enabled=False, output_stream=output_stream)
        
        logger.log_success(
            interaction_id="req_test",
            model="gpt-4",
            cost_metric={}
        )
        
        log_output = output_stream.getvalue()
        assert log_output == ""  # No output when disabled
    
    def test_log_emission_failure(self):
        """Test that log emission failures don't break the application."""
        output_stream = StringIO()
        
        # Mock json.dumps to raise an exception
        with patch('json.dumps', side_effect=Exception("JSON serialization failed")):
            logger = AuditLogger(enabled=True, output_stream=output_stream)
            
            # This should not raise an exception
            logger.log_success(
                interaction_id="req_test",
                model="gpt-4",
                cost_metric={}
            )
        
        # Should have written error to stderr
        # (we can't easily capture stderr in this test, but the main thing is no exception)
    
    def test_timestamp_format(self):
        """Test that timestamps are in ISO format with timezone."""
        output_stream = StringIO()
        logger = AuditLogger(enabled=True, output_stream=output_stream)
        
        logger.log_success(
            interaction_id="req_test",
            model="gpt-4",
            cost_metric={}
        )
        
        log_output = output_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        timestamp = log_data["timestamp"]
        # Should be ISO format ending with Z (UTC)
        assert timestamp.endswith('Z')
        # Should have proper ISO structure
        assert 'T' in timestamp  # Date and time separator