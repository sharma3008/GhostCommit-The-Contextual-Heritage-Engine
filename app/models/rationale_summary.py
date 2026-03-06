from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RationaleSummary(Base):
    __tablename__ = "rationale_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), index=True)
    pr_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="CASCADE"), index=True)

    summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)