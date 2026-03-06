from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.deps import get_db
from app.main import app
from app.models.pull_request import PullRequest
from app.models.repo import Repo
from app.models.tenant import Tenant


@pytest.fixture()
def client_and_session():
    """
    Creates an in-memory SQLite DB that persists across connections
    using StaticPool, and overrides FastAPI get_db dependency.
    Cleans up overrides after each test.
    """
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

    client = TestClient(app)
    try:
        yield client, TestingSessionLocal
    finally:
        app.dependency_overrides.clear()


def test_context_200(client_and_session):
    client, SessionLocal = client_and_session

    db = SessionLocal()
    t = Tenant(name="local")
    db.add(t)
    db.commit()
    db.refresh(t)

    r = Repo(
        tenant_id=t.id,
        provider="github",
        owner="sharma3008",
        name="GhostCommit-The-Contextual-Heritage-Engine",
    )
    db.add(r)
    db.commit()
    db.refresh(r)

    pr = PullRequest(
        tenant_id=t.id,
        repo_id=r.id,
        pr_number=42,
        title="Hello",
        author="karthik",
        state="open",
        raw_payload='{"x":1}',
    )
    db.add(pr)
    db.commit()
    db.close()

    res = client.get(
        "/context",
        params={
            "owner": "sharma3008",
            "repo": "GhostCommit-The-Contextual-Heritage-Engine",
            "pr": 42,
        },
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["repo"]["owner"] == "sharma3008"
    assert data["pull_request"]["pr_number"] == 42
    assert data["pull_request"]["raw_payload"] is None  # default: hidden


def test_context_include_raw(client_and_session):
    client, SessionLocal = client_and_session

    db = SessionLocal()
    t = Tenant(name="local")
    db.add(t)
    db.commit()
    db.refresh(t)

    r = Repo(
        tenant_id=t.id,
        provider="github",
        owner="sharma3008",
        name="GhostCommit-The-Contextual-Heritage-Engine",
    )
    db.add(r)
    db.commit()
    db.refresh(r)

    pr = PullRequest(
        tenant_id=t.id,
        repo_id=r.id,
        pr_number=101,
        title="Raw",
        author="karthik",
        state="open",
        raw_payload='{"secret":"nope"}',
    )
    db.add(pr)
    db.commit()
    db.close()

    res = client.get(
        "/context",
        params={
            "owner": "sharma3008",
            "repo": "GhostCommit-The-Contextual-Heritage-Engine",
            "pr": 101,
            "include_raw": True,
        },
    )
    assert res.status_code == 200, res.text
    assert res.json()["pull_request"]["raw_payload"] is not None


def test_context_404_repo(client_and_session):
    client, _ = client_and_session

    res = client.get("/context", params={"owner": "nope", "repo": "missing", "pr": 1})
    assert res.status_code == 404


def test_context_404_pr(client_and_session):
    client, SessionLocal = client_and_session

    db = SessionLocal()
    t = Tenant(name="local")
    db.add(t)
    db.commit()
    db.refresh(t)

    r = Repo(
        tenant_id=t.id,
        provider="github",
        owner="sharma3008",
        name="GhostCommit-The-Contextual-Heritage-Engine",
    )
    db.add(r)
    db.commit()
    db.close()

    res = client.get(
        "/context",
        params={
            "owner": "sharma3008",
            "repo": "GhostCommit-The-Contextual-Heritage-Engine",
            "pr": 999,
        },
    )
    assert res.status_code == 404