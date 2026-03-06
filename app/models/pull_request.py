from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PullRequest(Base):
    __tablename__ = "pull_requests"
    __table_args__ = (UniqueConstraint("repo_id", "pr_number", name="uq_pull_requests_repo_pr"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), index=True)

    pr_number: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(200), default="")
    state: Mapped[str] = mapped_column(String(50), default="open")  # open/closed/merged

    merged_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_payload: Mapped[str] = mapped_column(Text, default="")