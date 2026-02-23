import json

import structlog
from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.pull_request import PullRequest
from app.models.repo import Repo
from app.utils.github_sig import verify_github_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
log = structlog.get_logger()


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
):
    body = await request.body()

    ok = verify_github_signature(
        secret=settings.github_webhook_secret,
        body=body,
        signature_256=x_hub_signature_256,
    )

    if not ok:
        log.warning(
            "github_webhook_signature_invalid",
            delivery=x_github_delivery,
            github_event=x_github_event,
        )
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Only process pull_request events
    if x_github_event != "pull_request":
        return {"status": "ignored", "event": x_github_event}

    payload = json.loads(body.decode("utf-8"))
    action = payload.get("action")
    pr_data = payload.get("pull_request")

    if not pr_data:
        return {"status": "ignored", "reason": "no pull_request field"}

    owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]
    pr_number = pr_data["number"]

    db = SessionLocal()

    repo = db.scalar(
        select(Repo).where(
            Repo.owner == owner,
            Repo.name == repo_name,
        )
    )

    if not repo:
        log.warning("repo_not_found", owner=owner, repo=repo_name)
        return {"status": "repo_not_registered"}

    existing_pr = db.scalar(
        select(PullRequest).where(
            PullRequest.repo_id == repo.id,
            PullRequest.pr_number == pr_number,
        )
    )

    state = "merged" if pr_data.get("merged") else pr_data.get("state", "open")

    if existing_pr:
        existing_pr.title = pr_data.get("title", "")
        existing_pr.author = pr_data.get("user", {}).get("login", "")
        existing_pr.state = state
        existing_pr.raw_payload = json.dumps(payload)
        db.commit()
        pr_id = existing_pr.id
    else:
        new_pr = PullRequest(
            tenant_id=repo.tenant_id,
            repo_id=repo.id,
            pr_number=pr_number,
            title=pr_data.get("title", ""),
            author=pr_data.get("user", {}).get("login", ""),
            state=state,
            raw_payload=json.dumps(payload),
        )
        db.add(new_pr)
        db.commit()
        db.refresh(new_pr)
        pr_id = new_pr.id

    log.info("pr_ingested", pr_id=pr_id, action=action)

    return {"status": "stored", "pr_id": pr_id}