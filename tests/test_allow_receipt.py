from datetime import datetime, timezone

from pfc_boundary_proof.evaluator import evaluate_action
from pfc_boundary_proof.receipts import verify_receipt
from pfc_boundary_proof.scenarios import load_scenario


def test_valid_bounded_request_allows():
    action, policy = load_scenario("examples/ai_deploy_request.json")
    receipt = evaluate_action(action, policy)

    assert receipt.verdict == "ALLOW"
    assert receipt.reasons == ["request admitted"]
    verify_receipt(receipt, action, now=datetime(2026, 5, 24, 12, 2, tzinfo=timezone.utc))
