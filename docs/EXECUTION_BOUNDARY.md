# Execution Boundary

An execution boundary is a runtime admission point placed before consequence. It receives an action proposal, evaluates whether that proposal is admissible under a policy snapshot, and emits a signed receipt for the decision.

The boundary does not execute the action. It produces an admission artifact that can be verified before a downstream system performs any bounded effect.

## Admission Before Consequence

The sequence is:

```text
AI/system proposes action
PFC evaluates admissibility
PFC produces signed receipt
Verifier validates receipt
Action is admitted or refused
```

This differs from post-hoc audit. The decision is made before the action binds consequence. A refused action can still produce a receipt, but the receipt records that the proposal was denied under a defined policy, actor, context, and time window.

## Determinism

The proof uses canonical JSON and stable SHA-256 hashes for policy, payload, and context. Replaying the same action and policy at the receipt issue time must produce the same unsigned receipt fields and the same signature.

## Default Deny

The evaluator denies unless every required predicate is satisfied:

- actor is authorized
- policy is valid at evaluation time
- action type is in scope
- requested scope is in scope
- required evidence is present
- context is fresh
- request time bounds contain the evaluation time

No production capability is attached to this proof.
