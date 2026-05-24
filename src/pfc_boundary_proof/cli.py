"""Command line interface for the boundary proof."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from .canonical_json import canonical_json
from .evaluator import evaluate_action
from .models import BoundaryReceipt
from .receipts import ReceiptVerificationError, verify_receipt
from .replay import ReplayVerificationError, replay_decision
from .scenarios import load_action_document, load_json, load_policy_document, load_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PFC execution-boundary proof CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = subparsers.add_parser("evaluate", help="evaluate an action scenario")
    evaluate_parser.add_argument("scenario")

    verify_parser = subparsers.add_parser("verify-receipt", help="verify receipt against action")
    verify_parser.add_argument("receipt")
    verify_parser.add_argument("action")
    verify_parser.add_argument("--at", help="UTC verification time, defaults to receipt issued_at")

    replay_parser = subparsers.add_parser("replay", help="replay receipt decision")
    replay_parser.add_argument("receipt")
    replay_parser.add_argument("action")
    replay_parser.add_argument("policy")
    replay_parser.add_argument("--at", help="UTC verification time, defaults to receipt issued_at")

    args = parser.parse_args(argv)

    try:
        if args.command == "evaluate":
            action, policy = load_scenario(args.scenario)
            receipt = evaluate_action(action, policy)
            print(canonical_json(receipt.to_dict()))
            return 0

        if args.command == "verify-receipt":
            receipt = BoundaryReceipt.from_dict(load_json(args.receipt))
            action = load_action_document(args.action)
            verify_receipt(receipt, action, now=_verification_time(receipt, args.at))
            print("receipt verified")
            return 0

        if args.command == "replay":
            receipt = BoundaryReceipt.from_dict(load_json(args.receipt))
            action = load_action_document(args.action)
            policy = load_policy_document(args.policy)
            replay_decision(receipt, action, policy, now=_verification_time(receipt, args.at))
            print("replay verified")
            return 0
    except (KeyError, ReceiptVerificationError, ReplayVerificationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 1


def _verification_time(receipt: BoundaryReceipt, value: str | None) -> datetime:
    selected = value or receipt.issued_at
    return datetime.fromisoformat(selected.replace("Z", "+00:00")).astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())
