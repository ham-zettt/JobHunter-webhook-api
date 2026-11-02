from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    trigger: Mapped[str] = mapped_column(
        String(10), nullable=False, default="api", server_default="api"
    )
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="queued", server_default="queued"
    )
    requested_platforms: Mapped[str] = mapped_column(Text, nullable=False)
    params: Mapped[str] = mapped_column(Text, nullable=False)
    callback_url: Mapped[str | None] = mapped_column(Text)
    callback_status: Mapped[str | None] = mapped_column(String(10), default="pending")

    found_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    new_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    updated_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    duplicate_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    filtered_keyword: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    filtered_location: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    filtered_age: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(30), nullable=False)
    started_at: Mapped[str | None] = mapped_column(String(30))
    finished_at: Mapped[str | None] = mapped_column(String(30))

    __table_args__ = (
        CheckConstraint("trigger IN ('api','schedule')", name="ck_runs_trigger"),
        CheckConstraint(
            "status IN ('queued','running','completed','partial','failed','cancelled')",
            name="ck_runs_status",
        ),
        CheckConstraint(
            "callback_status IS NULL OR callback_status IN ('pending','sent','failed')",
            name="ck_runs_callback_status",
        ),
        CheckConstraint("json_valid(requested_platforms)", name="ck_runs_platforms_json"),
        CheckConstraint("json_valid(params)", name="ck_runs_params_json"),
        Index("ix_runs_created", text("created_at DESC")),
        Index("ix_runs_status", "status"),
    )


class ScrapeRunSource(Base):
    __tablename__ = "scrape_run_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("scrape_runs.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="queued", server_default="queued"
    )
    search_terms: Mapped[str | None] = mapped_column(Text)

    pages_visited: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    found_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    detail_fetched: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    new_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    updated_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    duplicate_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    filtered_keyword: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    filtered_location: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    filtered_age: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    error_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    errors: Mapped[str | None] = mapped_column(Text, default="[]")
    started_at: Mapped[str | None] = mapped_column(String(30))
    finished_at: Mapped[str | None] = mapped_column(String(30))

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','running','completed','degraded','blocked','auth_required',"
            "'failed','skipped','cancelled')",
            name="ck_run_sources_status",
        ),
        CheckConstraint("errors IS NULL OR json_valid(errors)", name="ck_run_sources_errors"),
        Index("uq_run_sources", "run_id", "platform", unique=True),
        Index("ix_run_sources_platform", "platform", text("finished_at DESC")),
    )


class JobRunLink(Base):
    __tablename__ = "job_run_links"

    run_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("scrape_runs.id", ondelete="CASCADE"), primary_key=True
    )
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[str] = mapped_column(String(30), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "action IN ('new','updated','seen','duplicate','repost')", name="ck_jrl_action"
        ),
        Index("ix_jrl_job", "job_id"),
    )
