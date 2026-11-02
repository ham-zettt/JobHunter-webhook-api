from __future__ import annotations

from sqlalchemy import func, select

from app.db.models import KeywordRule, LocationAlias
from app.db.session import SessionLocal
from app.seed.loader import seed_all


async def test_seed_is_idempotent():
    async with SessionLocal() as session:
        first = await seed_all(session)
        second = await seed_all(session)
        assert first["keywords"] > 0
        assert first["locations"] > 0
        assert second == {"keywords": 0, "locations": 0}
        kw = await session.scalar(select(func.count()).select_from(KeywordRule))
        loc = await session.scalar(select(func.count()).select_from(LocationAlias))
        assert kw == first["keywords"]
        assert loc == first["locations"]


async def test_seed_contains_strong_weak_and_exclude():
    async with SessionLocal() as session:
        await seed_all(session)
        strong = await session.scalar(
            select(func.count())
            .select_from(KeywordRule)
            .where(KeywordRule.type == "include", KeywordRule.strength == "strong")
        )
        weak = await session.scalar(
            select(func.count())
            .select_from(KeywordRule)
            .where(KeywordRule.type == "include", KeywordRule.strength == "weak")
        )
        exclude = await session.scalar(
            select(func.count()).select_from(KeywordRule).where(KeywordRule.type == "exclude")
        )
        assert strong >= 20
        assert weak >= 5
        assert exclude >= 30


async def test_seed_java_provinces():
    async with SessionLocal() as session:
        await seed_all(session)
        provinces = (
            await session.scalars(
                select(LocationAlias.province)
                .where(LocationAlias.alias_type == "province", LocationAlias.is_java == 1)
                .distinct()
            )
        ).all()
        assert set(provinces) == {
            "DKI Jakarta",
            "Banten",
            "Jawa Barat",
            "Jawa Tengah",
            "DI Yogyakarta",
            "Jawa Timur",
        }
