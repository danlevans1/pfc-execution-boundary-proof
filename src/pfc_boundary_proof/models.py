"""Typed models for the proof boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Verdict = Literal["ALLOW", "DENY"]


@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    action_type: str
    actor_id: str
    scope: str
    payload: dict[str, Any]
    context: dict[str, Any]
    evidence: dict[str, Any]
    requested_at: str
    not_before: str | None = None
    not_after: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActionProposal":
        return cls(
            action_id=data["action_id"],
            action_type=data["action_type"],
            actor_id=data["actor_id"],
            scope=data["scope"],
            payload=dict(data.get("payload", {})),
            context=dict(data.get("context", {})),
            evidence=dict(data.get("evidence", {})),
            requested_at=data["requested_at"],
            not_before=data.get("not_before"),
            not_after=data.get("not_after"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PolicySnapshot:
    policy_id: str
    policy_version: str
    authorized_actors: list[str]
    allowed_action_types: list[str]
    allowed_scopes: list[str]
    required_evidence: list[str]
    valid_from: str
    valid_until: str
    context_max_age_seconds: int
    receipt_ttl_seconds: int = 300

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolicySnapshot":
        return cls(
            policy_id=data["policy_id"],
            policy_version=data["policy_version"],
            authorized_actors=list(data.get("authorized_actors", [])),
            allowed_action_types=list(data.get("allowed_action_types", [])),
            allowed_scopes=list(data.get("allowed_scopes", [])),
            required_evidence=list(data.get("required_evidence", [])),
            valid_from=data["valid_from"],
            valid_until=data["valid_until"],
            context_max_age_seconds=int(data["context_max_age_seconds"]),
            receipt_ttl_seconds=int(data.get("receipt_ttl_seconds", 300)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BoundaryReceipt:
    decision_id: str
    action_id: str
    action_type: str
    actor_id: str
    policy_id: str
    policy_version: str
    policy_hash: str
    context_hash: str
    payload_hash: str
    verdict: Verdict
    reasons: list[str]
    issued_at: str
    expires_at: str
    key_id: str
    signature_algorithm: str
    signature: str = field(default="")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BoundaryReceipt":
        return cls(
            decision_id=data["decision_id"],
            action_id=data["action_id"],
            action_type=data["action_type"],
            actor_id=data["actor_id"],
            policy_id=data["policy_id"],
            policy_version=data["policy_version"],
            policy_hash=data["policy_hash"],
            context_hash=data["context_hash"],
            payload_hash=data["payload_hash"],
            verdict=data["verdict"],
            reasons=list(data.get("reasons", [])),
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            key_id=data["key_id"],
            signature_algorithm=data["signature_algorithm"],
            signature=data.get("signature", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def unsigned_dict(self) -> dict[str, Any]:
        data = self.to_dict()
        data.pop("signature", None)
        return data
