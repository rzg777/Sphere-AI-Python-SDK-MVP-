"""Unit tests for PolicyEngine and rule evaluation."""

import pytest
from unittest.mock import Mock

from sphere_ai.engine import (
    PolicyEngine, 
    PolicyConfig,
    ToolFilterRule, 
    RegexMaskRule,
    ContentFilterRule,
    EvaluationResult,
    Violation
)
from sphere_ai.client import InteractionContext
from sphere_ai.exceptions import SpherePolicyError


class TestPolicyEngine:
    """Test PolicyEngine rule evaluation."""
    
    def test_policy_engine_initialization(self):
        """Test PolicyEngine can be initialized with config."""
        config = PolicyConfig(
            version="1.0",
            security_rules=[
                {
                    "id": "test_rule",
                    "type": "tool_filter",
                    "action": "block",
                    "blocked_tools": ["bad_tool"]
                }
            ]
        )
        
        engine = PolicyEngine(config=config)
        assert len(engine.rules) == 1
        assert engine.rules[0].id == "test_rule"
    
    def test_tool_filter_pre_flight_blocking(self):
        """Test tool filter blocks dangerous tools in pre-flight."""
        rule = ToolFilterRule(
            id="block_dangerous",
            type="tool_filter",
            action="block",
            blocked_tools=["delete_user", "format_disk"]
        )
        engine = PolicyEngine(rules=[rule])
        
        context = InteractionContext(
            interaction_id="test",
            model="gpt-4",
            start_time=0.0,
            messages=[],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "delete_user",
                        "parameters": {}
                    }
                }
            ]
        )
        
        result = engine.evaluate_pre_flight(context)
        assert result.blocked is True
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "block_dangerous"
        assert result.violations[0].trigger == "delete_user"
    
    def test_tool_filter_pre_flight_allowed(self):
        """Test tool filter allows safe tools."""
        rule = ToolFilterRule(
            id="block_dangerous",
            type="tool_filter",
            action="block",
            blocked_tools=["delete_user"]
        )
        engine = PolicyEngine(rules=[rule])
        
        context = InteractionContext(
            interaction_id="test",
            model="gpt-4",
            start_time=0.0,
            messages=[],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "safe_tool",
                        "parameters": {}
                    }
                }
            ]
        )
        
        result = engine.evaluate_pre_flight(context)
        assert result.blocked is False
        assert len(result.violations) == 0
    
    def test_regex_mask_pre_flight_redaction(self):
        """Test regex mask redacts sensitive patterns."""
        rule = RegexMaskRule(
            id="mask_cc",
            type="regex_mask",
            action="redact",
            pattern="\\b\\d{4}[ -]?\\d{4}[ -]?\\d{4}[ -]?\\d{4}\\b",
            replacement="[REDACTED]"
        )
        engine = PolicyEngine(rules=[rule])
        
        original_messages = [
            {"role": "user", "content": "My card is 1234-5678-9012-3456"}
        ]
        
        context = InteractionContext(
            interaction_id="test",
            model="gpt-4",
            start_time=0.0,
            messages=original_messages,
            tools=None
        )
        
        result = engine.evaluate_pre_flight(context)
        assert result.blocked is False
        assert len(result.violations) == 1
        assert result.modified_messages is not None
        assert "[REDACTED]" in result.modified_messages[0]["content"]
        assert "1234-5678-9012-3456" not in result.modified_messages[0]["content"]
    
    def test_content_filter_blocking(self):
        """Test content filter blocks prohibited content."""
        rule = ContentFilterRule(
            id="block_secrets",
            type="content_filter",
            action="block",
            blocked_patterns=["api_key", "password"]
        )
        engine = PolicyEngine(rules=[rule])
        
        context = InteractionContext(
            interaction_id="test",
            model="gpt-4",
            start_time=0.0,
            messages=[
                {"role": "user", "content": "Here is my api_key: secret123"}
            ],
            tools=None
        )
        
        result = engine.evaluate_pre_flight(context)
        assert result.blocked is True
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "block_secrets"
    
    def test_rule_evaluation_order(self):
        """Test rules are evaluated in configuration order."""
        rule1 = ToolFilterRule(
            id="first_rule",
            type="tool_filter",
            action="block",
            blocked_tools=["tool_a"]
        )
        rule2 = ToolFilterRule(
            id="second_rule",
            type="tool_filter",
            action="block",
            blocked_tools=["tool_b"]
        )
        engine = PolicyEngine(rules=[rule1, rule2])
        
        context = InteractionContext(
            interaction_id="test",
            model="gpt-4",
            start_time=0.0,
            messages=[],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "tool_a",  # Should trigger first rule
                        "parameters": {}
                    }
                }
            ]
        )
        
        result = engine.evaluate_pre_flight(context)
        assert result.blocked is True
        # Should only have violation from first rule due to early termination
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "first_rule"
    
    def test_invalid_regex_pattern(self):
        """Test that invalid regex patterns raise proper error."""
        config = PolicyConfig(
            version="1.0",
            security_rules=[
                {
                    "id": "bad_regex",
                    "type": "regex_mask",
                    "action": "redact",
                    "pattern": "[invalid-regex"  # Unclosed character class
                }
            ]
        )
        
        with pytest.raises(SpherePolicyError):
            PolicyEngine(config=config)
    
    def test_empty_context_evaluation(self):
        """Test evaluation with empty context."""
        rule = ToolFilterRule(
            id="test_rule",
            type="tool_filter",
            action="block",
            blocked_tools=["some_tool"]
        )
        engine = PolicyEngine(rules=[rule])
        
        context = InteractionContext(
            interaction_id="test",
            model="gpt-4",
            start_time=0.0,
            messages=[],
            tools=None
        )
        
        result = engine.evaluate_pre_flight(context)
        assert result.blocked is False
        assert len(result.violations) == 0
        assert result.modified_messages is None


class TestEvaluationResult:
    """Test EvaluationResult dataclass behavior."""

    def test_evaluation_result_defaults(self):
        """Test EvaluationResult has proper defaults."""
        result = EvaluationResult()
        assert result.blocked is False
        assert result.violations == []
        assert result.modified_messages is None
    
    def test_evaluation_result_with_violations(self):
        """Test EvaluationResult with violations."""
        violation = Violation(
            rule_id="test_rule",
            trigger="test_trigger",
            type="tool_call"
        )
        result = EvaluationResult(
            blocked=True,
            violations=[violation]
        )
        assert result.blocked is True
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "test_rule"


class TestViolation:
    """Test Violation dataclass behavior."""
    
    def test_violation_creation(self):
        """Test Violation can be created with all fields."""
        violation = Violation(
            rule_id="test_rule",
            trigger="dangerous_tool",
            type="tool_call",
            compliance_tag="ISO_42001_A.9.4",
            details={"phase": "pre_flight"}
        )
        assert violation.rule_id == "test_rule"
        assert violation.trigger == "dangerous_tool"
        assert violation.type == "tool_call"
        assert violation.compliance_tag == "ISO_42001_A.9.4"
        assert violation.details == {"phase": "pre_flight"}
