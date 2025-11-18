"""Tests for policy pack implementations."""

from sphere_ai.policies import (
    hipaa_pack,
    owasp_top_10,
    pci_dss_pack,
    gdpr_pack
)
from sphere_ai.engine import (
    ToolFilterRule,
    RegexMaskRule,
    ContentFilterRule
)


class TestPolicyPacks:
    """Test that policy packs are properly implemented."""
    
    def test_hipaa_pack_implementation(self):
        """Test HIPAA policy pack structure and rules."""
        rules = hipaa_pack.get_rules()
        assert len(rules) == 4
        
        # Check rule types
        tool_rules = [r for r in rules if isinstance(r, ToolFilterRule)]
        regex_rules = [r for r in rules if isinstance(r, RegexMaskRule)]
        content_rules = [r for r in rules if isinstance(r, ContentFilterRule)]
        
        assert len(tool_rules) == 1
        assert len(regex_rules) == 2
        assert len(content_rules) == 1
        
        # Check specific rule properties
        phi_rule = tool_rules[0]
        assert "phi" in phi_rule.id
        assert len(phi_rule.blocked_tools) > 0
        assert "HIPAA" in phi_rule.compliance_tag
        
        ssn_rule = next(r for r in regex_rules if "ssn" in r.id)
        assert "\\d{3}-\\d{2}-\\d{4}" in ssn_rule.pattern
    
    def test_owasp_pack_implementation(self):
        """Test OWASP policy pack structure and rules."""
        rules = owasp_top_10.get_rules()
        assert len(rules) == 4
        
        tool_rules = [r for r in rules if isinstance(r, ToolFilterRule)]
        content_rules = [r for r in rules if isinstance(r, ContentFilterRule)]
        
        assert len(tool_rules) == 2
        assert len(content_rules) == 2
        
        # Check OWASP compliance tags
        for rule in rules:
            assert "OWASP" in rule.compliance_tag
        
        injection_rule = next(r for r in tool_rules if "injection" in r.id)
        assert len(injection_rule.blocked_tools) > 0
        assert "execute_sql" in injection_rule.blocked_tools
    
    def test_pci_dss_pack_implementation(self):
        """Test PCI DSS policy pack structure and rules."""
        rules = pci_dss_pack.get_rules()
        assert len(rules) == 5
        
        tool_rules = [r for r in rules if isinstance(r, ToolFilterRule)]
        regex_rules = [r for r in rules if isinstance(r, RegexMaskRule)]
        content_rules = [r for r in rules if isinstance(r, ContentFilterRule)]
        
        assert len(tool_rules) == 1
        assert len(regex_rules) == 3
        assert len(content_rules) == 1
        
        # Check PCI DSS compliance tags
        for rule in rules:
            assert "PCI_DSS" in rule.compliance_tag
        
        cc_rule = next(r for r in regex_rules if "credit_cards" in r.id)
        assert "\\d{13,16}" in cc_rule.pattern
    
    def test_gdpr_pack_implementation(self):
        """Test GDPR policy pack structure and rules."""
        rules = gdpr_pack.get_rules()
        assert len(rules) == 5
        
        tool_rules = [r for r in rules if isinstance(r, ToolFilterRule)]
        regex_rules = [r for r in rules if isinstance(r, RegexMaskRule)]
        content_rules = [r for r in rules if isinstance(r, ContentFilterRule)]
        
        assert len(tool_rules) == 1
        assert len(regex_rules) == 3
        assert len(content_rules) == 1
        
        # Check GDPR compliance tags
        for rule in rules:
            assert "GDPR" in rule.compliance_tag
        
        email_rule = next(r for r in regex_rules if "email" in r.id)
        assert "@" in email_rule.pattern
        
        special_category_rule = content_rules[0]
        assert len(special_category_rule.blocked_patterns) > 0
        assert "health data" in special_category_rule.blocked_patterns
    
    def test_policy_pack_rule_ids_unique(self):
        """Test that rule IDs are unique within each policy pack."""
        packs = [hipaa_pack, owasp_top_10, pci_dss_pack, gdpr_pack]
        
        for pack in packs:
            rules = pack.get_rules()
            rule_ids = [rule.id for rule in rules]
            assert len(rule_ids) == len(set(rule_ids)), f"Duplicate rule IDs in {pack.__class__.__name__}"
    
    def test_policy_pack_rule_actions(self):
        """Test that policy pack rules have appropriate actions."""
        packs = [hipaa_pack, owasp_top_10, pci_dss_pack, gdpr_pack]
        
        for pack in packs:
            rules = pack.get_rules()
            for rule in rules:
                # All policy pack rules should be either block or redact
                assert rule.action in ["block", "redact"]
                
                # Tool filter rules should be block actions
                if isinstance(rule, ToolFilterRule):
                    assert rule.action == "block"
                
                # Content filter rules should be block actions  
                if isinstance(rule, ContentFilterRule):
                    assert rule.action == "block"