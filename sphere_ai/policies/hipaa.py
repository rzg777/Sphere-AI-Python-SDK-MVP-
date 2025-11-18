"""HIPAA compliance policy pack for healthcare data protection."""

from ..engine import ToolFilterRule, RegexMaskRule, ContentFilterRule


# HIPAA Policy Pack
hipaa_pack = type('HIPAAPolicyPack', (), {
    'get_rules': lambda: [
        ToolFilterRule(
            id="hipaa_block_phi_access",
            type="tool_filter",
            action="block",
            blocked_tools=[
                "access_medical_records",
                "query_patient_data", 
                "export_health_data",
                "share_phi",
                "delete_medical_history"
            ],
            compliance_tag="HIPAA_164.308",
            description="Block tools that could access Protected Health Information"
        ),
        RegexMaskRule(
            id="hipaa_mask_ssn",
            type="regex_mask", 
            pattern="\\b\\d{3}-\\d{2}-\\d{4}\\b",
            action="redact",
            compliance_tag="HIPAA_164.312",
            description="Mask Social Security Numbers"
        ),
        RegexMaskRule(
            id="hipaa_mask_medical_ids",
            type="regex_mask",
            pattern="\\b\\d{10,}\\b",  # Simple pattern for medical record numbers
            action="redact", 
            compliance_tag="HIPAA_164.312",
            description="Mask medical record numbers and identifiers"
        ),
        ContentFilterRule(
            id="hipaa_block_phi_keywords",
            type="content_filter",
            action="block",
            blocked_patterns=[
                "medical record",
                "patient diagnosis", 
                "treatment plan",
                "health insurance",
                "prescription",
                "lab results"
            ],
            compliance_tag="HIPAA_164.306",
            description="Block content containing PHI keywords"
        )
    ]
})()