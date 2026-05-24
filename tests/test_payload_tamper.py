from datetime import datetime, timezone
from dataclasses import replace

import pytest

from pfc_boundary_proof.evaluator import evaluate_action
from pfc_boundary_proof.receipts import ReceiptVerificationError, verify_receipt
from pfc_boundary_proof.scenarios import load_scenario


def test_tampered_payload_fails_verification():
    action, policy = load_scenario("examples/ai_deploy_request.json")
    receipt = evaluate_action(action, policy)
    tampered = replace(action, payload={**action.payload, "artifact_digest": "sha256:tampered"})

    with pytest.raises(ReceiptVerificationError, match="payload hash mismatch"):
        verify_receipt(receipt, tampered, now=datetime(2026, 5, 24, 12, 2, tzinfo=timezone.utc))
