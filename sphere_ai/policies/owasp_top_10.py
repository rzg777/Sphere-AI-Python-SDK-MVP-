"""OWASP Top 10 security policy pack for web application security."""

from typing import List

from ..engine import BaseRule, ContentFilterRule, ToolFilterRule


def _owasp_rules() -> List[BaseRule]:
    return [
        ToolFilterRule(
            id="owasp_block_injection_tools",
            type="tool_filter",
            action="block",
            blocked_tools=[
                "execute_sql",
                "run_shell_command",
                "eval_code",
                "execute_script",
                "system_call",
            ],
            compliance_tag="OWASP_A03",
            description="Block tools that could enable injection attacks",
        ),
        ToolFilterRule(
            id="owasp_block_auth_bypass",
            type="tool_filter",
            action="block",
            blocked_tools=[
                "bypass_authentication",
                "elevate_privileges",
                "access_admin_panel",
                "reset_password_unauthorized",
            ],
            compliance_tag="OWASP_A07",
            description="Block tools that could bypass authentication",
        ),
        ContentFilterRule(
            id="owasp_block_sensitive_data_exposure",
            type="content_filter",
            action="block",
            blocked_patterns=[
                "api_key",
                "secret_key",
                "password",
                "private_key",
                "database_connection_string",
            ],
            compliance_tag="OWASP_A02",
            description="Block content containing sensitive credentials",
        ),
        ContentFilterRule(
            id="owasp_block_xxs_payloads",
            type="content_filter",
            action="block",
            blocked_patterns=[
                "<script>",
                "javascript:",
                "onload=",
                "onerror=",
                "onclick=",
            ],
            compliance_tag="OWASP_A03",
            description="Block potential XSS payload patterns",
        ),
    ]


class OWASPPolicyPack:
    """OWASP Top 10 rules packaged for reuse."""

    name = "OWASP_Top_10"
    description = "OWASP Top 10 secure development controls"

    def get_rules(self) -> List[BaseRule]:
        return list(_owasp_rules())


owasp_top_10 = OWASPPolicyPack()