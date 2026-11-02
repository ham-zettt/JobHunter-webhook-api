from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KeywordRule(Base):
    __tablename__ = "keyword_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(12), nullable=False)
    term: Mapped[str] = mapped_column(Text, nullable=False)
    strength: Mapped[str | None] = mapped_column(String(8))
    scope: Mapped[str] = mapped_column(
        String(12), nullable=False, default="both", server_default="both"
    )
    role_category: Mapped[str | None] = mapped_column(String(30))
    is_regex: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    is_active: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1")
    )
    source: Mapped[str] = mapped_column(
        String(8), nullable=False, default="seed", server_default="seed"
    )
    created_at: Mapped[str] = mapped_column(String(30), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(30), nullable=False)

    __table_args__ = (
        CheckConstraint("type IN ('include','exclude','search_term')", name="ck_kw_type"),
        CheckConstraint("strength IS NULL OR strength IN ('strong','weak')", name="ck_kw_strength"),
        CheckConstraint(
            "(type = 'include' AND strength IS NOT NULL) OR type <> 'include'",
            name="ck_kw_strength_required",
        ),
        CheckConstraint("scope IN ('title','description','both')", name="ck_kw_scope"),
        CheckConstraint("is_regex IN (0,1)", name="ck_kw_is_regex"),
        CheckConstraint("is_active IN (0,1)", name="ck_kw_is_active"),
        CheckConstraint("source IN ('seed','user')", name="ck_kw_source"),
        Index("ux_keyword_rules", "type", "term", "scope", unique=True),
        Index("ix_keyword_rules_active", "type", "is_active"),
    )


class LocationAlias(Base):
    __tablename__ = "location_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(Text, nullable=False)
    alias_type: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str | None] = mapped_column(Text)
    province: Mapped[str | None] = mapped_column(Text)
    is_java: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        CheckConstraint(
            "alias_type IN ('city','province','region','country_id','country_foreign',"
            "'remote_word')",
            name="ck_loc_type",
        ),
        CheckConstraint("is_java IS NULL OR is_java IN (0,1)", name="ck_loc_is_java"),
        Index("ux_loc_alias", "alias", "alias_type", unique=True),
        Index("ix_loc_alias", "alias"),
    )
