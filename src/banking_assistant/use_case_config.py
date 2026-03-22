"""Deployment-ready banking assistant use-case configuration.

This module mirrors the exploratory logic captured in the notebook so the
validated configuration can be reused in an application or API layer.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class Persona:
    name: str
    goals: List[str]
    channels: List[str]
    success_metrics: List[str]


@dataclass(frozen=True)
class UseCaseBlueprint:
    use_case_name: str
    business_problem: str
    priority_capabilities: List[str]
    required_data_sources: List[str]
    guardrails: List[str]
    personas: List[Persona]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


BANKING_ASSISTANT_BLUEPRINT = UseCaseBlueprint(
    use_case_name="Intelligent Banking Service and Relationship Assistant",
    business_problem=(
        "Improve service resolution time, empower relationship managers, and "
        "standardize high-volume banking support workflows with secure agentic AI."
    ),
    priority_capabilities=[
        "Intent understanding and task planning",
        "Secure tool orchestration across banking systems",
        "Retrieval-augmented generation over policies and SOPs",
        "Human-in-the-loop approvals for high-risk actions",
        "Personalized responses using customer and interaction context",
    ],
    required_data_sources=[
        "Core banking transactions",
        "CRM and relationship data",
        "Card servicing and dispute systems",
        "Loan origination status",
        "Internal product, policy, and SOP knowledge bases",
        "Fraud, AML, and case management signals",
    ],
    guardrails=[
        "Role-based access control and authentication",
        "PII masking and least-privilege tool access",
        "Audit logs for prompts, tool calls, and actions",
        "Grounded responses tied to trusted sources",
        "Human approval for sensitive decisions and irreversible actions",
    ],
    personas=[
        Persona(
            name="Retail banking customer",
            goals=[
                "Resolve account or card service requests quickly",
                "Understand transaction issues and next steps",
                "Receive accurate, compliant support across channels",
            ],
            channels=["Mobile app", "Online banking portal", "Contact center"],
            success_metrics=[
                "First-contact resolution",
                "Self-service completion rate",
                "Customer satisfaction",
            ],
        ),
        Persona(
            name="Relationship manager",
            goals=[
                "Prepare faster for client interactions",
                "Receive actionable next-best-action suggestions",
                "Access a concise 360-degree customer summary",
            ],
            channels=["RM desktop", "CRM workspace"],
            success_metrics=[
                "Preparation time saved",
                "Cross-sell conversion",
                "Advisor productivity",
            ],
        ),
        Persona(
            name="Operations analyst",
            goals=[
                "Route cases efficiently",
                "Validate documents against policy rules",
                "Escalate exceptions with complete context",
            ],
            channels=["Case management console", "Operations workflow tools"],
            success_metrics=[
                "Manual effort reduction",
                "Cycle time improvement",
                "Operational risk reduction",
            ],
        ),
    ],
)


def summarize_mvp_scope() -> Dict[str, List[str]]:
    """Return a practical MVP scope for the first delivery increment."""

    return {
        "journeys": [
            "Account and transaction inquiries",
            "Card dispute intake",
            "Service policy lookup",
            "Relationship manager meeting summaries",
        ],
        "tooling": [
            "Knowledge retrieval",
            "Case creation",
            "Customer context retrieval",
            "Human escalation workflow",
        ],
        "non_functional_requirements": [
            "Auditability",
            "Prompt and response monitoring",
            "Source grounding",
            "Access control",
        ],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(BANKING_ASSISTANT_BLUEPRINT.to_dict(), indent=2))
    print(json.dumps(summarize_mvp_scope(), indent=2))
