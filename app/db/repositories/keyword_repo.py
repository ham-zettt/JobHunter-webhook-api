from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.timeutil import utc_iso
from app.db.models import KeywordRule
from app.seed.loader import seed_keywords


def rule_dict(rule: KeywordRule) -> dict[str, Any]:
    return {
        "id": rule.id,
        "type": rule.type,
        "term": rule.term,
        "strength": rule.strength,
        "scope": rule.scope,
        "role_category": rule.role_category,
        "is_regex": bool(rule.is_regex),
        "is_active": bool(rule.is_active),
        "source": rule.source,
    }


async def list_rules(
    session: AsyncSession, *, type_: str | None = None, is_active: bool | None = None
) -> list[KeywordRule]:
    stmt = select(KeywordRule).order_by(KeywordRule.type, KeywordRule.id)
    if type_:
        stmt = stmt.where(KeywordRule.type == type_)
    if is_active is not None:
        stmt = stmt.where(KeywordRule.is_active == int(is_active))
    return list((await session.scalars(stmt)).all())


async def active_rules(session: AsyncSession) -> list[KeywordRule]:
    return list(
        (await session.scalars(select(KeywordRule).where(KeywordRule.is_active == 1))).all()
    )


async def search_terms(session: AsyncSession, limit: int) -> list[str]:
    rows = await session.scalars(
        select(KeywordRule.term)
        .where(KeywordRule.type == "search_term", KeywordRule.is_active == 1)
        .order_by(KeywordRule.id)
        .limit(limit)
    )
    return list(rows.all())


async def create_rule(session: AsyncSession, data: dict[str, Any]) -> KeywordRule:
    now = utc_iso()
    rule = KeywordRule(source="user", created_at=now, updated_at=now, **data)
    session.add(rule)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("Aturan kata kunci sudah ada") from exc
    await session.refresh(rule)
    return rule


async def update_rule(session: AsyncSession, rule_id: int, data: dict[str, Any]) -> KeywordRule:
    rule = await session.get(KeywordRule, rule_id)
    if rule is None:
        raise NotFoundError("Aturan kata kunci tidak ditemukan")
    for key, value in data.items():
        setattr(rule, key, value)
    rule.updated_at = utc_iso()
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("Aturan kata kunci bentrok dengan aturan lain") from exc
    await session.refresh(rule)
    return rule


async def delete_rule(session: AsyncSession, rule_id: int) -> None:
    rule = await session.get(KeywordRule, rule_id)
    if rule is None:
        raise NotFoundError("Aturan kata kunci tidak ditemukan")
    await session.delete(rule)
    await session.commit()


async def reseed(session: AsyncSession) -> dict[str, int]:
    await session.execute(delete(KeywordRule).where(KeywordRule.source == "seed"))
    await session.commit()
    try:
        added = await seed_keywords(session)
    except IntegrityError as exc:
        await session.rollback()
        raise ValidationAppError("Seed bentrok dengan aturan user") from exc
    return {"keywords": added}
