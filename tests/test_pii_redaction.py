from app.utils.pii import redact_json, redact_text


def test_redact_email_and_phone():
    s = "Email me at karthik@example.com or call +1 913-207-1660."
    res = redact_text(s)
    assert "[REDACTED_EMAIL]" in res.text
    assert "[REDACTED_PHONE]" in res.text
    assert res.counts["email"] >= 1
    assert res.counts["phone"] >= 1


def test_redact_github_token():
    s = "token=ghp_abcdefghijklmnopqrstuvwxyz1234567890ABCDE"
    res = redact_text(s)
    assert "[REDACTED_TOKEN]" in res.text or "[REDACTED_SECRET]" in res.text


def test_redact_private_key_block():
    s = """-----BEGIN PRIVATE KEY-----
ABCDEF123456
-----END PRIVATE KEY-----"""
    res = redact_text(s)
    assert "[REDACTED_PRIVATE_KEY]" in res.text
    assert res.counts["private_key_block"] >= 1


def test_redact_json_recursive():
    payload = {
        "a": "user email: test@example.com",
        "b": ["call 913-207-1660", {"k": "AKIA1234567890ABCDEF"}],
    }
    red, counts = redact_json(payload)
    assert "test@example.com" not in red["a"]
    assert "[REDACTED_EMAIL]" in red["a"]
    assert "[REDACTED_PHONE]" in red["b"][0]
    assert "[REDACTED_AWS_KEY_ID]" in red["b"][1]["k"]
    assert counts["email"] >= 1