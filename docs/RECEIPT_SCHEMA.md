# Receipt Schema

A receipt is a signed admission artifact. It binds the decision to an action, policy snapshot, actor, context, payload, and time window.

Required fields:

| Field | Meaning |
| --- | --- |
| `decision_id` | Stable hash-derived identifier for the decision. |
| `action_id` | Identifier of the proposed action. |
| `action_type` | Type of proposed action. |
| `actor_id` | Actor that proposed the action. |
| `policy_id` | Policy snapshot identifier. |
| `policy_version` | Policy snapshot version. |
| `policy_hash` | Canonical SHA-256 hash of the policy snapshot. |
| `context_hash` | Canonical SHA-256 hash of action context. |
| `payload_hash` | Canonical SHA-256 hash of action payload. |
| `verdict` | `ALLOW` or `DENY`. |
| `reasons` | Deterministic decision reasons. |
| `issued_at` | UTC issue time. |
| `expires_at` | UTC expiration time. |
| `key_id` | Signing key identifier. |
| `signature_algorithm` | Signature algorithm, `Ed25519` in this proof. |
| `signature` | Base64 Ed25519 signature over the unsigned receipt. |

The signature covers every field except `signature`.

The included key is a demo fixture marked unsafe for production. It exists only to make verification deterministic in this public proof.
