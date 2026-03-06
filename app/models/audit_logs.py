from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)

    action: Mapped[str] = mapped_column(String(200), index=True)
    actor: Mapped[str] = mapped_column(String(200), default="")
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())