from __future__ import annotations

import os
from datetime import datetime

import requests


BASE = os.environ.get("DEMO_BASE_URL", "http://localhost:8000")


def test_checkpoint_artifact_roundtrip():
    date = datetime.utcnow().strftime('%Y-%m-%d')
    r = requests.post(f"{BASE}/checkpoints/generate", params={"date": date})
    assert r.status_code == 200
    art = requests.get(f"{BASE}/checkpoints/artifacts/{date}")
    assert art.status_code == 200
    artifact = art.json()
    ver = requests.get(f"{BASE}/checkpoints/{date}/verify")
    assert ver.status_code == 200
    vr = ver.json()
    assert artifact.get('merkle_root') == vr.get('merkle_root')

