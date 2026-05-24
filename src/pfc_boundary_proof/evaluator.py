"""Default-deny execution-boundary evaluator."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .canonical_json import stable_hash
from .models import ActionProposal, BoundaryReceipt, PolicySnapshot, Verdict
from .receipts import DEMO_KEY_ID, SIGNATURE_ALGORITHM, sign_receipt


def evaluate_action(
    action: ActionProposal,
    policy: PolicySnapshot,
    *,
    now: datetime | None = None,
) -> BoundaryReceipt:
    evaluation_time = now or _parse_time(action.requested_at)
    reasons = _deny_reasons(action, policy, evaluation_time)
    verdict: Verdict = "ALLOW" if not reasons else "DENY"
    if verdict == "ALLOW":
        reasons = ["request admitted"]

    issued_at = _format_time(evaluation_time)
    expires_at = _format_time(evaluation_time + timedelta(seconds=policy.receipt_ttl_seconds))
    policy_hash = stable_hash(policy.to_dict())
    context_hash = stable_hash(action.context)
    payload_hash = stable_hash(action.payload)
    decision_id = stable_hash(
        {
            "action_id": action.action_id,
            "actor_id": action.actor_id,
            "context_hash": context_hash,
            "issued_at": issued_at,
            "payload_hash": payload_hash,
            "policy_hash": policy_hash,
            "verdict": verdict,
            "reasons": reasons,
        }
    )

    unsigned = BoundaryReceipt(
        decision_id=decision_id,
        action_id=action.action_id,
        action_type=action.action_type,
        actor_id=action.actor_id,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        policy_hash=policy_hash,
        context_hash=context_hash,
        payload_hash=payload_hash,
        verdict=verdict,
        reasons=reasons,
        issued_at=issued_at,
        expires_at=expires_at,
        key_id=DEMO_KEY_ID,
        signature_algorithm=SIGNATURE_ALGORITHM,
    )
    return sign_receipt(unsigned)


def _deny_reasons(
    action: ActionProposal,
    policy: PolicySnapshot,
    evaluation_time: datetime,
) -> list[str]:
    reasons: list[str] = []

    if not _within(evaluation_time, policy.valid_from, policy.valid_until):
        reasons.append("policy not valid at evaluation time")
    if action.actor_id not in policy.authorized_actors:
        reasons.append("actor not authorized")
    if action.action_type not in policy.allowed_action_types:
        reasons.append("action type outside policy")
    if action.scope not in policy.allowed_scopes:
        reasons.append("scope outside policy")

    missing = [name for name in policy.required_evidence if not action.evidence.get(name)]
    if missing:
        reasons.append("required evidence missing: " + ", ".join(sorted(missing)))

    observed_at = action.context.get("observed_at")
    if not isinstance(observed_at, str):
        reasons.append("context observed_at missing")
    else:
        age = evaluation_time - _parse_time(observed_at)
        if age < timedelta(seconds=0):
            reasons.append("context observed_at is in the future")
        if age > timedelta(seconds=policy.context_max_age_seconds):
            reasons.append("context stale")

    requested_at = _parse_time(action.requested_at)
    if requested_at > evaluation_time:
        reasons.append("request is from the future")
    if action.not_before and evaluation_time < _parse_time(action.not_before):
        reasons.append("request before not_before")
    if action.not_after and evaluation_time > _parse_time(action.not_after):
        reasons.append("request after not_after")

    return reasons


def _within(value: datetime, start: str, end: str) -> bool:
    return _parse_time(start) <= value <= _parse_time(end)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
