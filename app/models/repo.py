from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Repo(Base):
    __tablename__ = "repos"
    __table_args__ = (UniqueConstraint("tenant_id", "owner", "name", name="uq_repos_tenant_owner_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)

    provider: Mapped[str] = mapped_column(String(50), default="github")
    owner: Mapped[str] = mapped_column(String(200), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)

    tenant = relationship("Tenant")