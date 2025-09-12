from __future__ import annotations

from pathlib import Path

import sys
sys.path.append(str((Path(__file__).resolve().parent.parent / 'icn-node').resolve()))

from app.utils.crypto import sha256_hex, merkle_root


def test_merkle_root_small_chain(capsys):
    leaves = [sha256_hex(b'a'), sha256_hex(b'b'), sha256_hex(b'c')]
    print('Leaves:', leaves)
    root = merkle_root(leaves)
    print('Merkle root:', root)
    captured = capsys.readouterr()
    assert 'Merkle root:' in captured.out
    assert isinstance(root, str) and len(root) == 64


