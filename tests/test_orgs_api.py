from __future__ import annotations

import os

import requests


BASE = os.environ.get("DEMO_BASE_URL", "http://localhost:8000")


def test_orgs_returns_seeded():
    r = requests.get(f"{BASE}/orgs")
    assert r.status_code == 200
    data = r.json()
    items = data.get('items', [])
    # Expect at least 3 demo orgs
    assert len(items) >= 3
    assert all('org_id' in x and 'pubkey' in x for x in items)


