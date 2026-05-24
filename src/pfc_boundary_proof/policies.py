"""Policy fixtures for the public proof surface."""

from __future__ import annotations

from .models import PolicySnapshot


DEFAULT_POLICY = PolicySnapshot(
    policy_id="pfc-public-proof-policy",
    policy_version="2026-05-24.1",
    authorized_actors=["agent:release-bot", "system:payment-controller"],
    allowed_action_types=["deploy.preview", "payment.release"],
    allowed_scopes=["environment:preview", "payment:escrow-release"],
    required_evidence=["change_ticket", "risk_review"],
    valid_from="2026-05-24T00:00:00Z",
    valid_until="2026-05-25T00:00:00Z",
    context_max_age_seconds=300,
    receipt_ttl_seconds=300,
)
