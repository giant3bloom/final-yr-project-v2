import json
import socket
from typing import Any

from config import STATUS_HOST, STATUS_PORT

_SCORE_OMIT = object()


def log_message(
    text: str,
    status: bool,
    host: str = STATUS_HOST,
    port: int = STATUS_PORT,
    *,
    phase: str | None = None,
    score: float | None | object = _SCORE_OMIT,
    error: str | None = None,
    clear_error: bool = False,
) -> None:
    """Log locally and push status to the NexAI status shower."""
    message: dict[str, Any] = {"text": text, "status": status}
    if phase is not None:
        message["phase"] = phase
    if score is not _SCORE_OMIT:
        message["score"] = score
    if error:
        message["error"] = error
    if clear_error:
        message["clear_error"] = True

    status_msg = "SUCCESS" if status else "FAILED"
    print(f"[LOG] {text} -> {status_msg}")

    payload = json.dumps(message).encode("utf-8") + b"\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            sock.connect((host, port))
            sock.sendall(payload)
    except OSError as exc:
        print(f"[WARN] Status shower unreachable at {host}:{port} — {exc}")
