"""Tests for configuration loading and validation."""

import tempfile
import os
import pytest
from unittest.mock import patch

from sphere_ai.config import (
    load_config_from_yaml,
    merge_policies,
    validate_config_schema,
    create_default_config
)
from sphere_ai.engine import PolicyConfig
from sphere_ai.exceptions import SphereConfigurationError


class TestConfigLoading:
    """Test YAML configuration loading and validation."""
    
    def test_load_valid_config(self):
        """Test loading a valid YAML configuration."""
        config_content = """
        version: "1.0"
        compliance_standard: "ISO_42001"
        security_rules:
          - id: "test_rule"
            type: "tool_filter"
            action: "block"
            blocked_tools: ["bad_tool"]
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            config = load_config_from_yaml(temp_path)
            assert config.version == "1.0"
            assert config.compliance_standard == "ISO_42001"
            assert len(config.security_rules) == 1
            assert config.security_rules[0]["id"] == "test_rule"
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_file(self):
        """Test loading a non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            load_config_from_yaml("/nonexistent/path/sphere.yaml")
    
    def test_load_invalid_yaml(self):
        """Test loading invalid YAML content."""
        config_content = """
        version: "1.0"
        security_rules:
          - id: "test_rule"
            type: "tool_filter"
            action: "block"
            blocked_tools: ["bad_tool"]
        invalid: yaml: content
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            with pytest.raises(SphereConfigurationError):
                load_config_from_yaml(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_empty_config(self):
        """Test loading an empty configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with pytest.raises(SphereConfigurationError):
                load_config_from_yaml(temp_path)
        finally:
            os.unlink(temp_path)


class TestConfigValidation:
    """Test configuration schema validation."""
    
    def test_validate_valid_schema(self):
        """Test validation of valid configuration schema."""
        config_data = {
            "version": "1.0",
            "compliance_standard": "ISO_42001",
            "security_rules": [
                {
                    "id": "test_rule",
                    "type": "tool_filter",
                    "action": "block",
                    "blocked_tools": ["bad_tool"]
                }
            ]
        }
        
        # Should not raise an exception
        validate_config_schema(config_data)
    
    def test_validate_missing_version(self):
        """Test validation fails with missing version."""
        config_data = {
            "compliance_standard": "ISO_42001",
            "security_rules": []
        }
        
        with pytest.raises(SphereConfigurationError):
            validate_config_schema(config_data)
    
    def test_validate_invalid_security_rules(self):
        """Test validation fails with invalid security rules."""
        config_data = {
            "version": "1.0",
            "security_rules": "not_a_list"  # Should be a list
        }
        
        with pytest.raises(SphereConfigurationError):
            validate_config_schema(config_data)
    
    def test_validate_rule_missing_fields(self):
        """Test validation fails when rules miss required fields."""
        config_data = {
            "version": "1.0",
            "security_rules": [
                {
                    "type": "tool_filter",  # Missing id and action
                    "blocked_tools": ["bad_tool"]
                }
            ]
        }
        
        with pytest.raises(SphereConfigurationError):
            validate_config_schema(config_data)


class TestConfigMerging:
    """Test configuration merging logic."""
    
    def test_merge_policies_both_provided(self):
        """Test merging when both file and programmatic configs are provided."""
        file_config = PolicyConfig(
            version="1.0",
            compliance_standard="ISO_42001",
            security_rules=[{"id": "file_rule", "type": "tool_filter", "action": "block"}]
        )
        
        programmatic_config = PolicyConfig(
            version="1.1",
            compliance_standard="GDPR",
            security_rules=[{"id": "programmatic_rule", "type": "regex_mask", "action": "redact"}]
        )
        
        merged = merge_policies(file_config, programmatic_config)
        
        # Should prefer file config for version and compliance_standard
        assert merged.version == "1.0"
        assert merged.compliance_standard == "ISO_42001"
        # Should merge security rules (file rules first)
        assert len(merged.security_rules) == 2
        assert merged.security_rules[0]["id"] == "file_rule"
        assert merged.security_rules[1]["id"] == "programmatic_rule"
    
    def test_merge_policies_only_file(self):
        """Test merging when only file config is provided."""
        file_config = PolicyConfig(
            version="1.0",
            security_rules=[{"id": "file_rule", "type": "tool_filter", "action": "block"}]
        )
        
        merged = merge_policies(file_config, None)
        assert merged == file_config
    
    def test_merge_policies_only_programmatic(self):
        """Test merging when only programmatic config is provided."""
        programmatic_config = PolicyConfig(
            version="1.0",
            security_rules=[{"id": "programmatic_rule", "type": "tool_filter", "action": "block"}]
        )
        
        merged = merge_policies(None, programmatic_config)
        assert merged == programmatic_config
    
    def test_merge_policies_neither_provided(self):
        """Test merging when neither config is provided."""
        merged = merge_policies(None, None)
        assert isinstance(merged, PolicyConfig)
        assert merged.version == "1.0"
        assert merged.security_rules == []


class TestDefaultConfig:
    """Test default configuration creation."""
    
    def test_create_default_config(self):
        """Test creation of default configuration."""
        default_config = create_default_config()
        
        assert default_config.version == "1.0"
        assert default_config.compliance_standard == "ISO_42001"
        assert len(default_config.security_rules) == 2
        
        # Check specific rules exist
        rule_ids = [rule["id"] for rule in default_config.security_rules]
        assert "block_destructive_tools" in rule_ids
        assert "mask_credit_cards" in rule_ids