"""Session storage — JSON files in ~/.debrief/sessions/.

No database. Sessions are just JSON files, like how OpenClaw
stores config in ~/.openclaw/ and Hermes stores state in ~/.hermes/.
"""

import json
import uuid
from pathlib import Path

from debriefeur.config import get_sessions_dir


def create_session_id() -> str:
    """Generate a short session ID."""
    return str(uuid.uuid4())[:8]


def save_session(session_id: str, session: dict) -> Path:
    """Save session state to disk."""
    path = get_sessions_dir() / f"{session_id}.json"
    path.write_text(json.dumps(session, indent=2, default=str))
    return path


def load_session(session_id: str) -> dict | None:
    """Load session state from disk."""
    path = get_sessions_dir() / f"{session_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def list_sessions() -> list[dict]:
    """List all sessions with basic info."""
    sessions = []
    for path in sorted(get_sessions_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text())
            sessions.append({
                "id": path.stem,
                "status": data.get("status", "unknown"),
                "layer": data.get("current_layer", "unknown"),
                "started_at": data.get("started_at", "unknown"),
                "questions": sum(
                    lp.get("questions_asked", 0)
                    for lp in data.get("layer_progress", {}).values()
                ),
            })
        except Exception:
            continue
    return sessions
