# Sphere AI Python SDK

A production-grade Python SDK for LLM interception, agentic security, and governance compliance.

## Features

- **🔒 Agentic Security**: Block dangerous tool calls and redact sensitive data
- **📋 Compliance Logging**: Structured NDJSON audit logs with ISO 42001 tagging
- **⚡ Drop-in Wrapper**: Minimal code changes required
- **🏷️ Policy as Code**: Define security rules in YAML configuration
- **📦 Policy Packs**: Pre-packaged compliance modules (HIPAA, OWASP, PCI DSS, GDPR)
- **🔍 Local Evaluation**: No external network calls for policy decisions

## Installation

```bash
pip install sphere-ai
```

## Quick Start

```python
from openai import OpenAI
from sphere_ai import SphereClient
from sphere_ai.policies import hipaa_pack, owasp_top_10

# Wrap your existing OpenAI client
openai_client = OpenAI(api_key="your-api-key")
client = SphereClient(
    openai_client, 
    policies=[hipaa_pack, owasp_top_10],
    config_path="sphere.yaml"  # Optional
)

# Use exactly like the OpenAI client
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather today?"}],
    tools=[{"type": "function", "function": {"name": "get_weather", "parameters": {}}}]
)
```

## Configuration

Create a `sphere.yaml` file in your project root:

```yaml
version: "1.0"
compliance_standard: "ISO_42001"

security_rules:
  - id: "block_destructive_tools"
    type: "tool_filter"
    action: "block"
    blocked_tools: ["delete_user", "drop_db", "execute_shell"]
    compliance_tag: "ISO_42001_A.9.4"

  - id: "mask_credit_cards"
    type: "regex_mask"
    pattern: "\\b(?:\\d[ -]*?){13,16}\\b"
    action: "redact"
    compliance_tag: "GDPR_Art_32"
```

### Environment-Specific Configuration

```python
# Use environment variable
import os
os.environ["SPHERE_POLICY_PATH"] = "config/prod-sphere.yaml"

# Or specify directly
client = SphereClient(openai_client, config_path="config/staging-sphere.yaml")
```

## Policy Packs

```python
from sphere_ai.policies import (
    hipaa_pack,        # Healthcare data protection
    owasp_top_10,      # Web application security  
    pci_dss_pack,      # Payment card compliance
    gdpr_pack          # European data protection
)

client = SphereClient(openai_client, policies=[hipaa_pack, gdpr_pack])
```

## Audit Logs

The SDK emits structured NDJSON logs to stdout:

```json
{
  "timestamp": "2025-11-18T10:00:00Z",
  "level": "AUDIT",
  "source": "sphere_sdk",
  "model": "gpt-4-turbo",
  "interaction_id": "req_123abc",
  "policy_decision": "BLOCKED",
  "violation": {
    "rule_id": "block_destructive_tools",
    "trigger": "delete_user",
    "type": "tool_call"
  },
  "compliance": {
    "standard": "ISO_42001",
    "control_id": "A.9.4"
  },
  "cost_metric": {
    "prompt_tokens": 50,
    "completion_tokens": 10
  }
}
```

## Advanced Usage

### Custom Policies

```python
from sphere_ai.engine import PolicyEngine, ToolFilterRule, RegexMaskRule

# Create custom rules
custom_rules = [
    ToolFilterRule(
        id="block_custom_tools",
        blocked_tools=["dangerous_function"],
        action="block",
        compliance_tag="CUSTOM_001"
    ),
    RegexMaskRule(
        id="mask_custom_pattern",
        pattern="\\bCOMPANY-\\d{4}\\b",
        action="redact",
        compliance_tag="CUSTOM_002"
    )
]

# Create custom policy engine
engine = PolicyEngine(rules=custom_rules)
client = SphereClient(openai_client, policy_engine=engine)
```

### Programmatic Configuration

```python
from sphere_ai import SphereClient, PolicyConfig

config = PolicyConfig(
    version="1.0",
    compliance_standard="ISO_42001",
    security_rules=[
        {
            "id": "block_tools",
            "type": "tool_filter", 
            "action": "block",
            "blocked_tools": ["dangerous_tool"],
            "compliance_tag": "ISO_42001_A.9.4"
        }
    ]
)

client = SphereClient(openai_client, config=config)
```

### Disabling Audit Logging

```python
client = SphereClient(openai_client, enable_audit_logging=False)
```

## Rule Types

### Tool Filter Rules
Block specific function/tool calls by name:

```yaml
- id: "block_dangerous_operations"
  type: "tool_filter"
  action: "block"
  blocked_tools: ["delete_user", "execute_code", "format_disk"]
```

### Regex Mask Rules
Redact sensitive patterns in text:

```yaml
- id: "mask_pii"
  type: "regex_mask"
  pattern: "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN pattern
  action: "redact"
  replacement: "[REDACTED]"
```

### Content Filter Rules
Block messages containing specific content:

```yaml
- id: "block_sensitive_topics"
  type: "content_filter"
  action: "block"
  blocked_patterns: ["confidential", "trade secret", "proprietary"]
```

## Error Handling

```python
from sphere_ai.exceptions import SphereSecurityViolation

try:
    response = client.chat.completions.create(...)
except SphereSecurityViolation as e:
    print(f"Request blocked: {e}")
    # Handle security violation
except Exception as e:
    # Handle other errors
```

## Performance

The SDK is designed for minimal overhead:
- **Policy evaluation**: < 5ms for typical rule sets
- **Regex compilation**: Patterns are pre-compiled for performance
- **Early termination**: Blocking rules short-circuit evaluation

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=sphere_ai

# Type checking
mypy sphere_ai

# Format code
black sphere_ai tests
isort sphere_ai tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Apache 2.0