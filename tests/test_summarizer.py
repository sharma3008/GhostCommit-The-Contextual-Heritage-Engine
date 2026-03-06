from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.deps import get_db
from app.main import app
from app.models.pull_request import PullRequest
from app.models.rationale_summary import RationaleSummary
from app.models.repo import Repo
from app.models.tenant import Tenant


def make_client():
    engine = create_engine(
        "sqlite+pysqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestingSessionLocal


def test_generate_summary_stores_row_and_is_json():
    client, SessionLocal = make_client()
    db = SessionLocal()

    t = Tenant(name="local")
    db.add(t)
    db.commit()
    db.refresh(t)

    r = Repo(tenant_id=t.id, provider="github", owner="sharma3008", name="GhostCommit-The-Contextual-Heritage-Engine")
    db.add(r)
    db.commit()
    db.refresh(r)

    payload = {
        "repository": {"name": r.name, "owner": {"login": r.owner}},
        "pull_request": {"number": 7, "title": "Add summarizer", "user": {"login": "karthik"}},
        "contact": "karthik@example.com",
    }

    pr = PullRequest(
        tenant_id=t.id,
        repo_id=r.id,
        pr_number=7,
        title="Add summarizer",
        author="karthik",
        state="open",
        raw_payload=json.dumps(payload),
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)

    # Trigger generation
    res = client.post("/summaries/generate", params={"pr_id": pr.id})
    assert res.status_code == 200, res.text

    row = db.scalar(select(RationaleSummary).where(RationaleSummary.pr_id == pr.id).order_by(RationaleSummary.id.desc()))
    assert row is not None

    # Content must be valid JSON
    content = row.summary_json
    assert isinstance(content, str) and content
    parsed = json.loads(content)
    assert "summary" in parsed and "decision" in parsed
    db.close()


def teardown_module():
    app.dependency_overrides.clear()