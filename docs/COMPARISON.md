# Comparison

## Observability

Observability tells operators what happened inside a system. It is useful for diagnosis and operations, but it usually observes events after they occur.

Execution-boundary governance decides whether a proposed action is admissible before consequence.

## Audit Logging

Audit logging records activity for later inspection. It can show who did what and when, assuming the log remains trustworthy.

A boundary receipt is not a log line. It is a portable signed artifact binding a specific decision to a policy, actor, context, payload, and time window.

## Policy Engines

Policy engines evaluate rules and return decisions. They are often embedded into larger systems that decide how to use the result.

This proof narrows the pattern to runtime admission governance: the decision is signed, portable, replayable, and checked before bounded effect.

## Runtime Admission Governance

Runtime admission governance places a deterministic decision point between proposal and consequence:

```text
proposal -> evaluation -> signed receipt -> verification -> bounded effect or refusal
```

The signed receipt makes the decision independently verifiable and replayable from the original action and policy snapshot.
