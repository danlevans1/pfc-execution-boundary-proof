from datetime import datetime, timezone
from dataclasses import replace

import pytest

from pfc_boundary_proof.evaluator import evaluate_action
from pfc_boundary_proof.replay import ReplayVerificationError, replay_decision
from pfc_boundary_proof.scenarios import load_scenario


def test_replay_valid_receipt():
    action, policy = load_scenario("examples/ai_deploy_request.json")
    receipt = evaluate_action(action, policy)

    replay_decision(receipt, action, policy, now=datetime(2026, 5, 24, 12, 2, tzinfo=timezone.utc))


def test_replay_policy_mismatch_fails():
    action, policy = load_scenario("examples/ai_deploy_request.json")
    receipt = evaluate_action(action, policy)
    changed_policy = replace(policy, allowed_scopes=["payment:escrow-release"])

    with pytest.raises(ReplayVerificationError, match="policy hash mismatch"):
        replay_decision(
            receipt,
            action,
            changed_policy,
            now=datetime(2026, 5, 24, 12, 2, tzinfo=timezone.utc),
        )


def test_replay_changed_context_hash_fails():
    action, policy = load_scenario("examples/ai_deploy_request.json")
    receipt = evaluate_action(action, policy)
    changed_action = replace(action, context={**action.context, "workspace": "changed"})

    with pytest.raises(ReplayVerificationError, match="context hash mismatch"):
        replay_decision(
            receipt,
            changed_action,
            policy,
            now=datetime(2026, 5, 24, 12, 2, tzinfo=timezone.utc),
        )
