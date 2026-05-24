# Threat Model

This repository models attacks against a public execution-boundary proof surface. It does not model full production deployment infrastructure.

## Tampering

An attacker may alter an action payload after a receipt is issued. Verification recomputes `payload_hash` from the supplied action and rejects mismatches.

An attacker may alter context. Verification recomputes `context_hash` and rejects changed context.

An attacker may alter receipt fields. Signature verification rejects modified signed fields.

## Stale Context

An attacker may present old context as if it were current. The evaluator compares `context.observed_at` against the evaluation time and denies proposals outside the configured freshness window.

## Replay Mismatch

An attacker may try to reuse a receipt with a different action or policy snapshot. Replay recomputes the receipt from the original action and policy at the receipt issue time. Any mismatch fails.

## Scope Drift

An action may request an action type or scope outside the policy snapshot. The evaluator denies both cases by default.

## Unauthorized Actor

An actor not listed in the policy snapshot cannot receive an allow receipt. The denial is signed so the refusal remains portable and verifiable.

## Receipt Expiration

A receipt has an explicit expiration. Verification rejects receipts after `expires_at`, preventing stale admission artifacts from being reused indefinitely.
