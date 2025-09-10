from __future__ import annotations

import asyncio
from sqlalchemy import select
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
    for urn, name in DEMO_ORGS:
        exists = (await session.execute(select(Org).where(Org.urn == urn))).scalar_one_or_none()
        if exists:
            continue
        pub, priv = generate_keypair()
        org = Org(urn=urn, name=name, public_key=pub, metadata={"demo": True})
        session.add(org)
    await session.commit()


async def main() -> None:
    async with AsyncSessionFactory() as session:
        await seed_orgs(session)


if __name__ == "__main__":
    asyncio.run(main())


