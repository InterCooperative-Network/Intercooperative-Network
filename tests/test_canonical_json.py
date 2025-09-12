from __future__ import annotations

import json


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_stable_serialization_key_order():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonical(a) == canonical(b) == "{\"a\":1,\"b\":2}"


def test_stable_serialization_whitespace():
    a = {"a": [1, 2, 3], "m": {"z": 1, "y": 2}}
    s = canonical(a)
    assert "," in s and ":" in s
    assert " " not in s


