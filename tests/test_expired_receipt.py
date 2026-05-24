from datetime import datetime, timezone

import pytest

from pfc_boundary_proof.evaluator import evaluate_action
from pfc_boundary_proof.receipts import ReceiptVerificationError, verify_receipt
from pfc_boundary_proof.scenarios import load_scenario


def test_expired_receipt_fails_verification():
    action, policy = load_scenario("examples/ai_deploy_request.json")
    receipt = evaluate_action(action, policy)

    with pytest.raises(ReceiptVerificationError, match="receipt expired"):
        verify_receipt(receipt, action, now=datetime(2026, 5, 24, 12, 7, tzinfo=timezone.utc))
