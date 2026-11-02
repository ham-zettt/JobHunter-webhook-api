from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.timeutil import utc_iso
from app.db.models import KeywordRule, LocationAlias


def _load(name: str) -> dict[str, Any]:
    path = Path(get_settings().config_dir) / name
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _keyword_rows(data: dict[str, Any]) -> list[dict]:
    now = utc_iso()
    rows: list[dict] = []
    for term in data.get("search_terms", []):
        rows.append(
            dict(
                type="search_term",
                term=term.lower(),
                strength=None,
                scope="both",
                role_category=None,
                is_regex=0,
                is_active=1,
                source="seed",
                created_at=now,
                updated_at=now,
            )
        )
    for item in data.get("include", []):
        rows.append(
            dict(
                type="include",
                term=item["term"].lower(),
                strength=item["strength"],
                scope=item.get("scope", "both"),
                role_category=item.get("role_category"),
                is_regex=0,
                is_active=1,
                source="seed",
                created_at=now,
                updated_at=now,
            )
        )
    for term in data.get("exclude", []):
        rows.append(
            dict(
                type="exclude",
                term=term.lower(),
                strength=None,
                scope="title",
                role_category=None,
                is_regex=0,
                is_active=1,
                source="seed",
                created_at=now,
                updated_at=now,
            )
        )
    return rows


def _location_rows(data: dict[str, Any]) -> list[dict]:
    rows: list[dict] = []

    def add(
        alias: str, alias_type: str, city: str | None, province: str | None, is_java: int | None
    ) -> None:
        rows.append(
            dict(
                alias=alias.strip().lower(),
                alias_type=alias_type,
                city=city,
                province=province,
                is_java=is_java,
            )
        )

    for prov in data.get("provinces", []):
        pname = prov["name"]
        jv = int(prov.get("is_java", 1))
        add(pname, "province", None, pname, jv)
        for alias in prov.get("aliases", []):
            add(alias, "province", None, pname, jv)
        for region in prov.get("regions", []):
            add(region, "region", None, pname, jv)
        for city in prov.get("cities", []):
            add(city["name"], "city", city["name"], pname, jv)
            for alias in city.get("aliases", []):
                add(alias, "city", city["name"], pname, jv)

    for pname in data.get("outside_java_provinces", []):
        add(pname, "province", None, pname, 0)
    for city in data.get("outside_java_cities", []):
        add(city["name"], "city", city["name"], city["province"], 0)
    for alias in data.get("country_id", []):
        add(alias, "country_id", None, None, None)
    for alias in data.get("country_foreign", []):
        add(alias, "country_foreign", None, None, None)
    for alias in data.get("remote_words", []):
        add(alias, "remote_word", None, None, None)
    return rows


async def seed_keywords(session: AsyncSession) -> int:
    rows = _keyword_rows(_load("keywords.yaml"))
    existing = {
        (r.type, r.term, r.scope) for r in (await session.scalars(select(KeywordRule))).all()
    }
    added = 0
    for row in rows:
        key = (row["type"], row["term"], row["scope"])
        if key in existing:
            continue
        session.add(KeywordRule(**row))
        existing.add(key)
        added += 1
    await session.commit()
    return added


async def seed_locations(session: AsyncSession) -> int:
    rows = _location_rows(_load("locations_java.yaml"))
    existing = {
        (r.alias, r.alias_type) for r in (await session.scalars(select(LocationAlias))).all()
    }
    added = 0
    for row in rows:
        key = (row["alias"], row["alias_type"])
        if key in existing:
            continue
        session.add(LocationAlias(**row))
        existing.add(key)
        added += 1
    await session.commit()
    return added


async def seed_all(session: AsyncSession) -> dict[str, int]:
    return {
        "keywords": await seed_keywords(session),
        "locations": await seed_locations(session),
    }
