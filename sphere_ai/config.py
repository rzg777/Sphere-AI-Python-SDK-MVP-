"""YAML configuration loading and schema validation for Sphere AI policies."""

import yaml
from typing import Any, Dict, Optional
from pathlib import Path

from .engine import PolicyConfig
from .exceptions import SphereConfigurationError


def load_config_from_yaml(config_path: str) -> PolicyConfig:
    """
    Load policy configuration from YAML file.
    
    Args:
        config_path: Path to the sphere.yaml configuration file
        
    Returns:
        PolicyConfig: Loaded policy configuration
        
    Raises:
        SphereConfigurationError: If the file is invalid or malformed
        FileNotFoundError: If the file doesn't exist
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        if not config_data:
            raise SphereConfigurationError("Configuration file is empty")
        
        # Validate required fields
        if 'version' not in config_data:
            raise SphereConfigurationError("Missing required field: version")
        
        # Convert to PolicyConfig
        return PolicyConfig(**config_data)
        
    except yaml.YAMLError as e:
        raise SphereConfigurationError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        raise SphereConfigurationError(f"Failed to load configuration: {e}")


def merge_policies(
    file_config: Optional[PolicyConfig], 
    programmatic_config: Optional[PolicyConfig]
) -> PolicyConfig:
    """
    Merge file-based and programmatic policy configurations.
    
    Args:
        file_config: Configuration from YAML file
        programmatic_config: Programmatically provided configuration
        
    Returns:
        PolicyConfig: Merged configuration
    """
    if file_config and programmatic_config:
        # Merge security rules from both sources
        merged_rules = file_config.security_rules + programmatic_config.security_rules
        
        # Use programmatic config as base, but keep file version if not specified
        base_config = programmatic_config.copy()
        base_config.security_rules = merged_rules
        
        if not base_config.compliance_standard and file_config.compliance_standard:
            base_config.compliance_standard = file_config.compliance_standard
            
        return base_config
    
    elif file_config:
        return file_config
    elif programmatic_config:
        return programmatic_config
    else:
        # Return empty default config
        return PolicyConfig()


def validate_config_schema(config_data: Dict[str, Any]) -> None:
    """
    Validate configuration schema.
    
    Args:
        config_data: Configuration data to validate
        
    Raises:
        SphereConfigurationError: If schema validation fails
    """
    required_fields = ['version']
    
    for field in required_fields:
        if field not in config_data:
            raise SphereConfigurationError(f"Missing required field: {field}")
    
    if 'security_rules' in config_data:
        if not isinstance(config_data['security_rules'], list):
            raise SphereConfigurationError("security_rules must be a list")
        
        for i, rule in enumerate(config_data['security_rules']):
            if not isinstance(rule, dict):
                raise SphereConfigurationError(f"Rule {i} must be a dictionary")
            
            if 'id' not in rule:
                raise SphereConfigurationError(f"Rule {i} missing required field: id")
            
            if 'type' not in rule:
                raise SphereConfigurationError(f"Rule {i} missing required field: type")
            
            if 'action' not in rule:
                raise SphereConfigurationError(f"Rule {i} missing required field: action")


def create_default_config() -> PolicyConfig:
    """Create a default policy configuration with basic security rules."""
    return PolicyConfig(
        version="1.0",
        compliance_standard="ISO_42001",
        security_rules=[
            {
                "id": "block_destructive_tools",
                "type": "tool_filter",
                "action": "block",
                "blocked_tools": ["delete_user", "drop_db", "execute_shell", "format_disk"],
                "compliance_tag": "ISO_42001_A.9.4",
                "description": "Block dangerous system operations"
            },
            {
                "id": "mask_credit_cards",
                "type": "regex_mask", 
                "pattern": "\\b(?:\\d[ -]*?){13,16}\\b",
                "action": "redact",
                "compliance_tag": "PCI_DSS_3.4",
                "description": "Mask credit card numbers"
            }
        ]
    )