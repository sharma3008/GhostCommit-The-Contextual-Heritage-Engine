#!/usr/bin/env bash
set -euo pipefail

echo "==> Bringing stack up"
docker compose up -d --build >/dev/null

echo "==> Health/Ready"
curl -s http://localhost:8000/health
echo
curl -s http://localhost:8000/ready
echo

echo "==> OpenAPI routes"
curl -s http://localhost:8000/openapi.json | python - <<'PY'
import sys,json
d=json.load(sys.stdin)
print(sorted(d["paths"].keys()))
PY

echo "==> Alembic current/heads"
docker compose exec -T api alembic current
docker compose exec -T api alembic heads

echo "==> Unsigned webhook should be 401"
curl -i -s -X POST http://localhost:8000/webhooks/github -d '{"ping":"pong"}' | head -n 12

echo "==> Signed PR ingestion should be 200"
SECRET="${GITHUB_WEBHOOK_SECRET:-change-me}"
BODY='{"action":"opened","repository":{"name":"GhostCommit-The-Contextual-Heritage-Engine","owner":{"login":"sharma3008"}},"pull_request":{"number":999,"title":"Smoke Test PR","state":"open","merged":false,"user":{"login":"karthik"}}}'
SIG="sha256=$(printf "%s" "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk "{print \$2}")"

printf "%s" "$BODY" | curl -i -s -X POST http://localhost:8000/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: $SIG" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-GitHub-Delivery: smoke-test" \
  --data-binary @- | head -n 20

echo "==> DB check"
docker compose exec -T db psql -U ghostcommit -d ghostcommit -c "select pr_number,title,state from pull_requests order by id desc limit 3;"

echo "==> PII redaction check"
python - <<'PY'
from app.utils.pii import redact_text
s="Email: karthik@example.com Phone: +1 913-207-1660 Token: ghp_abcdefghijklmnopqrstuvwxyz1234567890ABCDE"
res=redact_text(s)
print(res.text)
print(res.counts)
PY

echo "✅ Smoke test complete."
