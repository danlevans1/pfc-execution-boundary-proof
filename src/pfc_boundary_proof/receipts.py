"""Ed25519 receipt signing and verification with demo-only fixture keys."""

from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone

from .canonical_json import canonical_json_bytes, stable_hash
from .models import ActionProposal, BoundaryReceipt

DEMO_KEY_ID = "demo-ed25519-unsafe-for-production"
SIGNATURE_ALGORITHM = "Ed25519"

# Demo fixture seed. Public proof only. Never use for production authority.
_DEMO_PRIVATE_SEED = bytes.fromhex(
    "000102030405060708090a0b0c0d0e0f"
    "101112131415161718191a1b1c1d1e1f"
)

_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _Q - 2, _Q)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)
_B = (
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960,
)


class ReceiptVerificationError(ValueError):
    pass


def sign_receipt(receipt: BoundaryReceipt) -> BoundaryReceipt:
    signature = _ed25519_sign(_DEMO_PRIVATE_SEED, canonical_json_bytes(receipt.unsigned_dict()))
    data = receipt.to_dict()
    data["signature"] = base64.b64encode(signature).decode("ascii")
    return BoundaryReceipt.from_dict(data)


def verify_signature(receipt: BoundaryReceipt) -> None:
    if receipt.key_id != DEMO_KEY_ID:
        raise ReceiptVerificationError("unknown key_id")
    if receipt.signature_algorithm != SIGNATURE_ALGORITHM:
        raise ReceiptVerificationError("unsupported signature algorithm")
    try:
        signature = base64.b64decode(receipt.signature.encode("ascii"), validate=True)
    except ValueError as exc:
        raise ReceiptVerificationError("invalid receipt signature") from exc
    public_key = _ed25519_public_key(_DEMO_PRIVATE_SEED)
    if not _ed25519_verify(public_key, canonical_json_bytes(receipt.unsigned_dict()), signature):
        raise ReceiptVerificationError("invalid receipt signature")


def verify_receipt(
    receipt: BoundaryReceipt,
    action: ActionProposal,
    *,
    now: datetime | None = None,
) -> None:
    verify_signature(receipt)

    if receipt.action_id != action.action_id:
        raise ReceiptVerificationError("action_id mismatch")
    if receipt.action_type != action.action_type:
        raise ReceiptVerificationError("action_type mismatch")
    if receipt.actor_id != action.actor_id:
        raise ReceiptVerificationError("actor_id mismatch")
    if receipt.payload_hash != stable_hash(action.payload):
        raise ReceiptVerificationError("payload hash mismatch")
    if receipt.context_hash != stable_hash(action.context):
        raise ReceiptVerificationError("context hash mismatch")

    verification_time = now or datetime.now(timezone.utc)
    if verification_time > _parse_time(receipt.expires_at):
        raise ReceiptVerificationError("receipt expired")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _inv(value: int) -> int:
    return pow(value, _Q - 2, _Q)


def _x_recover(y: int) -> int:
    xx = (y * y - 1) * _inv(_D * y * y + 1)
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * _I) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


def _point_add(point: tuple[int, int], other: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = point
    x2, y2 = other
    denominator = _D * x1 * x2 * y1 * y2
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + denominator)
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - denominator)
    return x3 % _Q, y3 % _Q


def _point_mul(scalar: int, point: tuple[int, int]) -> tuple[int, int]:
    result = (0, 1)
    addend = point
    while scalar:
        if scalar & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        scalar >>= 1
    return result


def _point_compress(point: tuple[int, int]) -> bytes:
    x, y = point
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _point_decompress(data: bytes) -> tuple[int, int] | None:
    if len(data) != 32:
        return None
    y = int.from_bytes(data, "little") & ((1 << 255) - 1)
    x = _x_recover(y)
    if (x & 1) != (data[31] >> 7):
        x = _Q - x
    if (y * y - x * x - 1 - _D * x * x * y * y) % _Q != 0:
        return None
    return x, y


def _secret_expand(seed: bytes) -> tuple[int, bytes]:
    if len(seed) != 32:
        raise ValueError("Ed25519 seed must be 32 bytes")
    digest = bytearray(_sha512(seed))
    digest[0] &= 248
    digest[31] &= 63
    digest[31] |= 64
    return int.from_bytes(digest[:32], "little"), bytes(digest[32:])


def _ed25519_public_key(seed: bytes) -> bytes:
    scalar, _ = _secret_expand(seed)
    return _point_compress(_point_mul(scalar, _B))


def _ed25519_sign(seed: bytes, message: bytes) -> bytes:
    scalar, prefix = _secret_expand(seed)
    public_key = _ed25519_public_key(seed)
    r = int.from_bytes(_sha512(prefix + message), "little") % _L
    encoded_r = _point_compress(_point_mul(r, _B))
    k = int.from_bytes(_sha512(encoded_r + public_key + message), "little") % _L
    s = (r + k * scalar) % _L
    return encoded_r + int.to_bytes(s, 32, "little")


def _ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    if len(public_key) != 32 or len(signature) != 64:
        return False
    encoded_r = signature[:32]
    s = int.from_bytes(signature[32:], "little")
    if s >= _L:
        return False
    point_a = _point_decompress(public_key)
    point_r = _point_decompress(encoded_r)
    if point_a is None or point_r is None:
        return False
    k = int.from_bytes(_sha512(encoded_r + public_key + message), "little") % _L
    return _point_mul(s, _B) == _point_add(point_r, _point_mul(k, point_a))
