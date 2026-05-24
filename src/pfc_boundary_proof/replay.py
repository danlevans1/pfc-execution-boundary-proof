"""Replay verifier for deterministic boundary decisions."""

from __future__ import annotations

from datetime import datetime

from .canonical_json import stable_hash
from .evaluator import evaluate_action
from .models import ActionProposal, BoundaryReceipt, PolicySnapshot
from .receipts import ReceiptVerificationError, verify_receipt


class ReplayVerificationError(ValueError):
    pass


def replay_decision(
    receipt: BoundaryReceipt,
    action: ActionProposal,
    policy: PolicySnapshot,
    *,
    now: datetime | None = None,
) -> None:
    try:
        verify_receipt(receipt, action, now=now)
    except ReceiptVerificationError as exc:
        raise ReplayVerificationError(str(exc)) from exc

    if receipt.policy_hash != stable_hash(policy.to_dict()):
        raise ReplayVerificationError("policy hash mismatch")

    recomputed = evaluate_action(action, policy, now=_parse_time(receipt.issued_at))
    if recomputed.unsigned_dict() != receipt.unsigned_dict():
        raise ReplayVerificationError("replayed decision does not match receipt")
    if recomputed.signature != receipt.signature:
        raise ReplayVerificationError("replayed signature does not match receipt")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
