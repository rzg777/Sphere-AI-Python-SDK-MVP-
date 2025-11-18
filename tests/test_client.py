"""Integration tests for SphereClient wrapper."""

import json
import sys
from io import StringIO
from unittest.mock import Mock, patch
import pytest

from sphere_ai import SphereClient
from sphere_ai.client import InteractionContext
from sphere_ai.engine import PolicyConfig, ToolFilterRule
from sphere_ai.exceptions import SphereSecurityViolation
from sphere_ai.policies import hipaa_pack


class TestSphereClient:
    """Test SphereClient integration with OpenAI client."""
    
    def test_sphere_client_initialization(self):
        """Test SphereClient can be initialized with OpenAI client."""
        mock_openai = Mock()
        client = SphereClient(mock_openai)
        
        assert client._openai_client == mock_openai
        assert hasattr(client, 'policy_engine')
        assert hasattr(client, 'audit_logger')
    
    def test_sphere_client_with_policy_packs(self):
        """Test SphereClient initialization with policy packs."""
        mock_openai = Mock()
        client = SphereClient(mock_openai, policies=[hipaa_pack])
        
        # Should have HIPAA rules loaded
        assert len(client.policy_engine.rules) > 0
        hipaa_rules = [r for r in client.policy_engine.rules if 'hipaa' in r.id]
        assert len(hipaa_rules) > 0
    
    def test_sphere_client_delegation(self):
        """Test that SphereClient delegates non-chat methods to OpenAI client."""
        mock_openai = Mock()
        mock_openai.models = Mock()
        mock_openai.models.list.return_value = ['model1', 'model2']
        
        client = SphereClient(mock_openai)
        result = client.models.list()
        
        assert result == ['model1', 'model2']
        mock_openai.models.list.assert_called_once()
    
    def test_chat_completion_interception_blocked(self):
        """Test that blocked tool calls raise SphereSecurityViolation."""
        mock_openai = Mock()
        
        # Configure mock to return a response (though it shouldn't be reached)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.tool_calls = None
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Create client with blocking rule
        blocking_rule = ToolFilterRule(
            id="test_block",
            type="tool_filter",
            action="block",
            blocked_tools=["dangerous_tool"]
        )
        client = SphereClient(
            mock_openai, 
            policy_engine=Mock(rules=[blocking_rule])
        )
        
        # Attempt to use blocked tool
        with pytest.raises(SphereSecurityViolation):
            client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Do something"}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "dangerous_tool",
                        "parameters": {}
                    }
                }]
            )
        
        # OpenAI API should not be called when blocked
        mock_openai.chat.completions.create.assert_not_called()
    
    def test_audit_logging_on_success(self):
        """Test that successful interactions generate audit logs."""
        mock_openai = Mock()
        
        # Configure mock response
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 5
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Hello"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage = mock_usage
        
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Capture stdout for logging
        captured_output = StringIO()
        client = SphereClient(
            mock_openai,
            enable_audit_logging=True
        )
        client.audit_logger.output_stream = captured_output
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Verify response
        assert response == mock_response
        
        # Verify audit log was written
        log_output = captured_output.getvalue().strip()
        assert log_output
        log_data = json.loads(log_output)
        assert log_data["policy_decision"] == "ALLOWED"
        assert log_data["model"] == "gpt-4"
        assert "interaction_id" in log_data
    
    def test_interaction_context_creation(self):
        """Test InteractionContext is properly created from API call."""
        mock_openai = Mock()
        client = SphereClient(mock_openai)
        
        # Mock the create method to capture context
        original_create = client._original_chat_completions.create
        captured_context = None
        
        def mock_create(**kwargs):
            # Create context like the real method would
            nonlocal captured_context
            captured_context = InteractionContext(
                interaction_id="test_id",
                model=kwargs.get("model", "unknown"),
                start_time=0.0,
                messages=kwargs.get("messages", []),
                tools=kwargs.get("tools"),
                tool_choice=kwargs.get("tool_choice")
            )
            return original_create(**kwargs)
        
        client._original_chat_completions.create = mock_create
        
        # Make API call
        test_messages = [{"role": "user", "content": "test"}]
        test_tools = [{"type": "function", "function": {"name": "test_tool", "parameters": {}}}]
        
        client.chat.completions.create(
            model="gpt-4",
            messages=test_messages,
            tools=test_tools,
            tool_choice="auto"
        )
        
        # Verify context
        assert captured_context is not None
        assert captured_context.model == "gpt-4"
        assert captured_context.messages == test_messages
        assert captured_context.tools == test_tools
        assert captured_context.tool_choice == "auto"