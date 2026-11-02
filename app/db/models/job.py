from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

PLATFORMS = ("linkedin", "kitalulus", "glints", "kalibrr", "dealls", "pintarnya", "jobstreet")
ROLE_CATEGORIES = (
    "frontend",
    "backend",
    "fullstack",
    "software_engineer",
    "ai_engineer",
    "ai_automation",
    "other_it",
)
WORK_MODES = ("remote", "onsite", "hybrid", "unknown")
EMPLOYMENT_TYPES = ("fulltime", "parttime", "contract", "freelance", "internship", "unknown")

_in_platforms = ", ".join(f"'{p}'" for p in PLATFORMS)
_in_roles = ", ".join(f"'{p}'" for p in ROLE_CATEGORIES)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text, nullable=False)
    url_canonical: Mapped[str] = mapped_column(Text, nullable=False)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    title_normalized: Mapped[str] = mapped_column(Text, nullable=False)
    company_name: Mapped[str | None] = mapped_column(Text)
    company_normalized: Mapped[str | None] = mapped_column(Text)

    location_raw: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    province: Mapped[str | None] = mapped_column(Text)
    is_in_java: Mapped[int | None] = mapped_column(Integer)
    is_indonesia: Mapped[int | None] = mapped_column(Integer)
    location_verified: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    work_mode: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown", server_default="unknown"
    )
    employment_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unknown", server_default="unknown"
    )

    salary_raw: Mapped[str | None] = mapped_column(Text)
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)
    salary_currency: Mapped[str | None] = mapped_column(String(8))
    salary_period: Mapped[str | None] = mapped_column(String(8))

    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    description_html: Mapped[str | None] = mapped_column(Text)
    description_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    description_truncated: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    posted_at: Mapped[str | None] = mapped_column(String(10))
    posted_at_precision: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown", server_default="unknown"
    )
    expires_at: Mapped[str | None] = mapped_column(String(10))
    effective_date: Mapped[str] = mapped_column(String(10), nullable=False)

    role_category: Mapped[str | None] = mapped_column(String(30))
    matched_keywords: Mapped[str | None] = mapped_column(Text)
    relevance_score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    fingerprint: Mapped[str] = mapped_column(String(40), nullable=False)
    is_duplicate: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    duplicate_of_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="SET NULL")
    )
    duplicate_reason: Mapped[str | None] = mapped_column(String(20))
    repost_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="active", server_default="active"
    )
    missed_runs: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    first_seen_at: Mapped[str] = mapped_column(String(30), nullable=False)
    last_seen_at: Mapped[str] = mapped_column(String(30), nullable=False)
    detail_fetched_at: Mapped[str | None] = mapped_column(String(30))
    first_run_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("scrape_runs.id", ondelete="SET NULL")
    )
    last_run_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("scrape_runs.id", ondelete="SET NULL")
    )

    created_at: Mapped[str] = mapped_column(String(30), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(30), nullable=False)
    raw_payload: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(f"platform IN ({_in_platforms})", name="ck_jobs_platform"),
        CheckConstraint(
            "work_mode IN ('remote','onsite','hybrid','unknown')", name="ck_jobs_work_mode"
        ),
        CheckConstraint(
            "employment_type IN ('fulltime','parttime','contract','freelance',"
            "'internship','unknown')",
            name="ck_jobs_employment_type",
        ),
        CheckConstraint(
            "posted_at_precision IN ('exact','date','relative','unknown')",
            name="ck_jobs_posted_precision",
        ),
        CheckConstraint("status IN ('active','expired','archived')", name="ck_jobs_status"),
        CheckConstraint(
            f"role_category IS NULL OR role_category IN ({_in_roles})", name="ck_jobs_role"
        ),
        CheckConstraint(
            "salary_period IS NULL OR salary_period IN ('hour','day','week','month','year')",
            name="ck_jobs_salary_period",
        ),
        CheckConstraint(
            "duplicate_reason IS NULL OR duplicate_reason IN ('cross_platform','repost')",
            name="ck_jobs_duplicate_reason",
        ),
        CheckConstraint("is_in_java IS NULL OR is_in_java IN (0,1)", name="ck_jobs_in_java"),
        CheckConstraint(
            "is_indonesia IS NULL OR is_indonesia IN (0,1)", name="ck_jobs_is_indonesia"
        ),
        CheckConstraint("location_verified IN (0,1)", name="ck_jobs_location_verified"),
        CheckConstraint("is_duplicate IN (0,1)", name="ck_jobs_is_duplicate"),
        CheckConstraint("description_truncated IN (0,1)", name="ck_jobs_desc_truncated"),
        CheckConstraint(
            "matched_keywords IS NULL OR json_valid(matched_keywords)",
            name="ck_jobs_matched_keywords",
        ),
        CheckConstraint(
            "(is_duplicate = 0 AND duplicate_of_id IS NULL) OR is_duplicate = 1",
            name="ck_jobs_duplicate_consistency",
        ),
        Index(
            "ux_jobs_platform_external",
            "platform",
            "external_id",
            unique=True,
            sqlite_where=text("external_id IS NOT NULL"),
        ),
        Index("ux_jobs_platform_urlcanon", "platform", "url_canonical", unique=True),
        Index("ix_jobs_listing", "status", "is_duplicate", text("effective_date DESC")),
        Index("ix_jobs_effective_date", "effective_date"),
        Index("ix_jobs_first_seen", "first_seen_at"),
        Index("ix_jobs_platform", "platform", "status"),
        Index("ix_jobs_fingerprint", "fingerprint"),
        Index("ix_jobs_company_norm", "company_normalized"),
        Index("ix_jobs_role", "role_category"),
        Index("ix_jobs_province", "province"),
        Index("ix_jobs_work_mode", "work_mode"),
        Index("ix_jobs_dup_of", "duplicate_of_id"),
        Index("ix_jobs_last_run", "last_run_id"),
    )
