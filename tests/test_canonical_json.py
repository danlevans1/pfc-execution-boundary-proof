from pfc_boundary_proof.canonical_json import canonical_json, stable_hash


def test_canonical_json_sorts_keys_and_removes_spacing():
    left = {"b": 2, "a": {"d": 4, "c": 3}}
    right = {"a": {"c": 3, "d": 4}, "b": 2}

    assert canonical_json(left) == '{"a":{"c":3,"d":4},"b":2}'
    assert canonical_json(left) == canonical_json(right)
    assert stable_hash(left) == stable_hash(right)
