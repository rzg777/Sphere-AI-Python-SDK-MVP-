"""GDPR compliance policy pack for European data protection."""

from ..engine import RegexMaskRule, ToolFilterRule, ContentFilterRule


# GDPR Policy Pack
gdpr_pack = type('GDPRPolicyPack', (), {
    'get_rules': lambda: [
        RegexMaskRule(
            id="gdpr_mask_email",
            type="regex_mask",
            pattern="\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            action="redact",
            compliance_tag="GDPR_Art_5",
            description="Mask email addresses"
        ),
        RegexMaskRule(
            id="gdpr_mask_phone",
            type="regex_mask",
            pattern="\\b(?:\\+?\\d{1,3}[-.\\s]?)?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}\\b",
            action="redact",
            compliance_tag="GDPR_Art_4",
            description="Mask phone numbers"
        ),
        RegexMaskRule(
            id="gdpr_mask_ip_address",
            type="regex_mask",
            pattern="\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b",
            action="redact",
            compliance_tag="GDPR_Recital_30",
            description="Mask IP addresses"
        ),
        ToolFilterRule(
            id="gdpr_block_data_export",
            type="tool_filter",
            action="block",
            blocked_tools=[
                "export_user_data",
                "bulk_data_download",
                "share_personal_data",
                "transfer_to_third_party"
            ],
            compliance_tag="GDPR_Art_44",
            description="Block unauthorized data export operations"
        ),
        ContentFilterRule(
            id="gdpr_block_special_category_data",
            type="content_filter",
            action="block",
            blocked_patterns=[
                "racial origin",
                "political opinions",
                "religious beliefs",
                "sexual orientation",
                "health data",
                "biometric data"
            ],
            compliance_tag="GDPR_Art_9",
            description="Block special category personal data"
        )
    ]
})()