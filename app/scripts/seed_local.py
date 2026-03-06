from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.repo import Repo
from app.models.tenant import Tenant


def main() -> None:
    db = SessionLocal()

    tenant_name = "local"
    owner = "sharma3008"
    repo_name = "GhostCommit-The-Contextual-Heritage-Engine"

    tenant = db.scalar(select(Tenant).where(Tenant.name == tenant_name))
    if not tenant:
        tenant = Tenant(name=tenant_name)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    repo = db.scalar(
        select(Repo).where(
            Repo.tenant_id == tenant.id,
            Repo.owner == owner,
            Repo.name == repo_name,
        )
    )
    if not repo:
        repo = Repo(tenant_id=tenant.id, provider="github", owner=owner, name=repo_name)
        db.add(repo)
        db.commit()
        db.refresh(repo)

    print(f"Seeded tenant={tenant.id}:{tenant.name}, repo={repo.id}:{repo.owner}/{repo.name}")


if __name__ == "__main__":
    main()