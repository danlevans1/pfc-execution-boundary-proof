from pfc_boundary_proof.evaluator import evaluate_action
from pfc_boundary_proof.scenarios import load_scenario


def test_stale_context_denied():
    action, policy = load_scenario("examples/stale_context_request.json")
    receipt = evaluate_action(action, policy)

    assert receipt.verdict == "DENY"
    assert "context stale" in receipt.reasons


def test_unauthorized_actor_denied():
    action, policy = load_scenario("examples/unauthorized_actor_request.json")
    receipt = evaluate_action(action, policy)

    assert receipt.verdict == "DENY"
    assert "actor not authorized" in receipt.reasons


def test_missing_evidence_denied():
    action, policy = load_scenario("examples/missing_evidence_request.json")
    receipt = evaluate_action(action, policy)

    assert receipt.verdict == "DENY"
    assert "required evidence missing: risk_review" in receipt.reasons
