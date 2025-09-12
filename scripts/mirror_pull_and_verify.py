from __future__ import annotations

import os
import sys
from urllib.request import urlopen, Request
import json


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/mirror_pull_and_verify.py BASE_URL YYYY-MM-DD")
        sys.exit(2)
    base = sys.argv[1].rstrip('/')
    date = sys.argv[2]
    try:
        with urlopen(Request(f"{base}/checkpoints/artifacts/{date}")) as r:
            artifact = json.loads(r.read().decode('utf-8'))
    except Exception:
        print(f"Artifact not found for {date}")
        sys.exit(1)
    with urlopen(Request(f"{base}/checkpoints/{date}/verify")) as r:
        vr = json.loads(r.read().decode('utf-8'))
    if vr.get('merkle_root') == artifact.get('merkle_root') and vr.get('ok'):
        print(f"OK {date} root={artifact.get('merkle_root')}")
        sys.exit(0)
    else:
        print("Mismatch or verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main()


