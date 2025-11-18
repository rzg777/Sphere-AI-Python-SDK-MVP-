# Sphere AI Python SDK

A production-grade Python SDK for LLM interception, agentic security, and governance compliance.

## Features

- **🔒 Agentic Security**: Block dangerous tool calls and redact sensitive data
- **📋 Compliance Logging**: Structured NDJSON audit logs with ISO 42001 tagging
- **⚡ Drop-in Wrapper**: Minimal code changes required
- **🏷️ Policy as Code**: Define security rules in YAML configuration
- **📦 Policy Packs**: Pre-packaged compliance modules (HIPAA, OWASP, etc.)

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
    config_path="sphere.yaml"
)

# Use exactly like the OpenAI client
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather today?"}],
    tools=[{"type": "function", "function": {"name": "get_weather", "parameters": {}}}]
)
```

## Configuration

Create a `sphere.yaml` file:

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

## Policy Packs

```python
from sphere_ai.policies import (
    hipaa_pack,
    owasp_top_10,
    pci_dss_pack,
    gdpr_pack
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
from sphere_ai.engine import PolicyEngine, ToolFilterRule

custom_rule = ToolFilterRule(
    id="block_custom_tools",
    blocked_tools=["dangerous_function"],
    action="block",
    compliance_tag="CUSTOM_001"
)

engine = PolicyEngine(rules=[custom_rule])
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

## License

Apache 2.0