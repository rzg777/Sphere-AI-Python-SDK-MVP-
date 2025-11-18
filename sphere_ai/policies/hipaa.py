"""HIPAA compliance policy pack for healthcare data protection."""

from typing import List

from ..engine import BaseRule, ContentFilterRule, RegexMaskRule, ToolFilterRule


def _hipaa_rules() -> List[BaseRule]:
    return [
        ToolFilterRule(
            id="hipaa_block_phi_access",
            type="tool_filter",
            action="block",
            blocked_tools=[
                "access_medical_records",
                "query_patient_data",
                "export_health_data",
                "share_phi",
                "delete_medical_history",
            ],
            compliance_tag="HIPAA_164.308",
            description="Block tools that could access Protected Health Information",
        ),
        RegexMaskRule(
            id="hipaa_mask_ssn",
            type="regex_mask",
            pattern="\\b\\d{3}-\\d{2}-\\d{4}\\b",
            action="redact",
            compliance_tag="HIPAA_164.312",
            description="Mask Social Security Numbers",
        ),
        RegexMaskRule(
            id="hipaa_mask_medical_ids",
            type="regex_mask",
            pattern="\\b\\d{10,}\\b",
            action="redact",
            compliance_tag="HIPAA_164.312",
            description="Mask medical record numbers and identifiers",
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
                "lab results",
            ],
            compliance_tag="HIPAA_164.306",
            description="Block content containing PHI keywords",
        ),
    ]


class HIPAAPolicyPack:
    """Materialized policy pack for HIPAA controls."""

    name = "HIPAA"
    description = "Healthcare data protection controls"

    def get_rules(self) -> List[BaseRule]:
        """Return a new list of HIPAA rules."""
        return list(_hipaa_rules())


hipaa_pack = HIPAAPolicyPack()