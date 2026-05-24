# PFC Execution Boundary Proof

[![CI](https://github.com/danevans/pfc-execution-boundary-proof/actions/workflows/ci.yml/badge.svg)](https://github.com/danevans/pfc-execution-boundary-proof/actions/workflows/ci.yml)

Public proof surface for PFC-style execution-boundary governance and signed runtime admission receipts.

This repository demonstrates deterministic admission control before an action can bind consequence. It is intentionally narrow: no production adapters, no deployment authority, no network mutation, no credential access, and no proprietary PFC internals.

## What this repo demonstrates

An AI system, agent, or automation layer proposes an action. The boundary evaluates the proposal against a policy snapshot, signs a receipt for the decision, and allows downstream verification before any bounded effect is attempted.

The core path is:

```text
proposal -> evaluation -> signed receipt -> verification -> bounded effect or refusal
```

The implementation proves:

- deterministic canonical JSON hashing
- default-deny policy evaluation
- Ed25519 signed receipts using demo-only fixture keys
- portable verification of payload, context, signature, and expiration
- replay verification against the original action and policy snapshot

## Execution-boundary model

The boundary is a runtime admission point. It evaluates a proposed action before the action is allowed to bind consequence.

Inputs:

- proposed action
- actor identity
- requested scope
- evidence
- context freshness
- immutable policy snapshot
- evaluation time window

Output:

- `ALLOW` or `DENY`
- deterministic reasons
- a signed receipt binding the decision to the action, actor, policy, context, payload, and time window

Default behavior is deny. An action is admitted only when the actor is authorized, the policy is valid, scope is valid, evidence is present, context is fresh, and the request is inside the configured time bounds.

## Why receipts are different from logs

“Receipt ≠ log entry.
A receipt is portable cryptographic proof that a specific action was admitted or refused under a defined policy, actor, context, and time window.”

Logs describe what a system observed or recorded. A receipt is an admission artifact produced before effect. It is signed, portable, and independently verifiable.

| System type | Flow |
| --- | --- |
| Traditional agent systems | proposal -> tool call -> logs |
| PFC-style execution boundary | proposal -> evaluation -> signed receipt -> verification -> bounded effect or refusal |

## Threat assumptions

This proof assumes an attacker may try to tamper with payloads, reuse receipts, submit stale context, drift scope, change policy snapshots, or act as an unauthorized principal. The verifier rejects those cases by recomputing canonical hashes, checking the receipt signature, enforcing expiration, and replaying the decision from the original inputs.

This proof does not claim to secure real production execution. It demonstrates the public, deterministic boundary pattern only.

## Example flow

```bash
python -m pfc_boundary_proof.cli evaluate examples/ai_deploy_request.json > receipt.json
python -m pfc_boundary_proof.cli verify-receipt receipt.json examples/ai_deploy_request.json
python -m pfc_boundary_proof.cli replay receipt.json examples/ai_deploy_request.json examples/ai_deploy_request.json
```

The example request file contains both an `action` and a `policy` snapshot. The replay command accepts either a plain policy snapshot or an example file containing a top-level `policy` object.

## CLI examples

Evaluate a bounded deployment proposal:

```bash
python -m pfc_boundary_proof.cli evaluate examples/ai_deploy_request.json
```

Verify a receipt against the original action request:

```bash
python -m pfc_boundary_proof.cli verify-receipt receipt.json action.json
```

Replay the decision against the original action and policy snapshot:

```bash
python -m pfc_boundary_proof.cli replay receipt.json action.json policy.json
```

## Replay guarantees

Replay recomputes the decision from:

- original action
- policy snapshot
- receipt issue time

Replay fails if:

- payload hash changes
- context hash changes
- policy hash changes
- receipt signature is invalid
- receipt is expired
- recomputed verdict or reasons differ
- recomputed receipt fields do not match the signed receipt

## Safety constraints

- Demo-only Ed25519 fixture key, labeled unsafe for production.
- No credential loading.
- No network actions.
- No Git actions.
- No deployment, payment, or production adapters.
- No autonomous execution.
- No hidden authority.

## Non-goals

This repository is not a production authorization service, not a deployment controller, not an observability product, and not a post-hoc audit log. It is a compact engineering proof of admission-before-consequence governance.
