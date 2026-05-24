from dataclasses import replace

from pfc_boundary_proof.canonical_json import stable_hash
from pfc_boundary_proof.scenarios import load_scenario


def test_policy_hash_is_stable_and_changes_on_policy_change():
    _, policy = load_scenario("examples/ai_deploy_request.json")

    assert stable_hash(policy.to_dict()) == stable_hash(policy.to_dict())
    assert stable_hash(policy.to_dict()) != stable_hash(
        replace(policy, policy_version="changed").to_dict()
    )
