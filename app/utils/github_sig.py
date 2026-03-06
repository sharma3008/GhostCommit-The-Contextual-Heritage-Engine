import hashlib
import hmac


def verify_github_signature(secret: str, body: bytes, signature_256: str | None) -> bool:
    """
    GitHub sends: X-Hub-Signature-256: sha256=<hexdigest>
    """
    if not secret:
        return False
    if not signature_256:
        return False
    if not signature_256.startswith("sha256="):
        return False

    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    provided = signature_256.split("sha256=", 1)[1].strip()

    # constant-time compare
    return hmac.compare_digest(expected, provided)