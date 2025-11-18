"""PCI DSS compliance policy pack for payment card data protection."""

from ..engine import RegexMaskRule, ToolFilterRule, ContentFilterRule


# PCI DSS Policy Pack
pci_dss_pack = type('PCIDSSToolFilterRule', (), {
    'get_rules': lambda: [
        RegexMaskRule(
            id="pci_mask_credit_cards",
            type="regex_mask",
            pattern="\\b(?:\\d[ -]*?){13,16}\\b",
            action="redact",
            compliance_tag="PCI_DSS_3.4",
            description="Mask primary account numbers (PAN)"
        ),
        RegexMaskRule(
            id="pci_mask_cvv",
            type="regex_mask",
            pattern="\\b\\d{3,4}\\b",  # CVV/CVC codes
            action="redact",
            compliance_tag="PCI_DSS_3.2",
            description="Mask card verification values"
        ),
        RegexMaskRule(
            id="pci_mask_track_data",
            type="regex_mask",
            pattern="\\b%?[A-Z0-9=]+\\^[A-Z0-9/]+\\?",  # Simplified track data pattern
            action="redact",
            compliance_tag="PCI_DSS_3.2.1",
            description="Mask magnetic stripe track data"
        ),
        ToolFilterRule(
            id="pci_block_payment_operations",
            type="tool_filter",
            action="block",
            blocked_tools=[
                "process_payment",
                "authorize_transaction",
                "capture_funds",
                "refund_payment",
                "store_credit_card"
            ],
            compliance_tag="PCI_DSS_6.4",
            description="Block payment processing operations"
        ),
        ContentFilterRule(
            id="pci_block_sensitive_auth_data",
            type="content_filter",
            action="block",
            blocked_patterns=[
                "card verification value",
                "magnetic stripe",
                "PIN block",
                "CAV2/CVC2/CVV2/CID"
            ],
            compliance_tag="PCI_DSS_3.2",
            description="Block sensitive authentication data references"
        )
    ]
})()