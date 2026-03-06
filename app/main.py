from fastapi import FastAPI

from app.api.context import router as context_router
from app.api.health import router as health_router
from app.api.summaries import router as summaries_router
from app.api.webhooks import router as webhooks_router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="GhostCommit API", version="0.1.0")

app.include_router(health_router)
app.include_router(webhooks_router)
app.include_router(context_router)
app.include_router(summaries_router)
