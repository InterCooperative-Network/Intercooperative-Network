from __future__ import annotations

import asyncio
from sqlalchemy import select
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from .db import AsyncSessionFactory, engine
from .models import Org
from .utils.crypto import generate_keypair


DEMO_ORGS = [
    ("urn:coop:sunrise-bakery", "Sunrise Bakery Cooperative"),
    ("urn:coop:river-housing", "River Housing Cooperative"),
    ("urn:coop:valley-food", "Valley Food Cooperative"),
]


async def seed_orgs(session: AsyncSession) -> None:
    demo_keys: dict[str, dict[str, str]] = {}
    for urn, name in DEMO_ORGS:
        exists = (await session.execute(select(Org).where(Org.urn == urn))).scalar_one_or_none()
        if exists:
            continue
        pub, priv = generate_keypair()
        org = Org(urn=urn, name=name, public_key=pub, metadata={"demo": True})
        session.add(org)
        demo_keys[urn] = {"public_key": pub, "private_key": priv}
    await session.commit()
    if demo_keys:
        # Persist keys for local testing
        out = Path(__file__).resolve().parent.parent / "demo_keys.json"
        with open(out, "w") as f:
            json.dump(demo_keys, f, indent=2)
        for urn, keys in demo_keys.items():
            print(f"Created {urn}")
            print(f"  Public Key: {keys['public_key']}")
            print(f"  Private Key: {keys['private_key']}")
            print("---")


async def main() -> None:
    async with AsyncSessionFactory() as session:
        await seed_orgs(session)


if __name__ == "__main__":
    asyncio.run(main())


