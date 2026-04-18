"""Configuration — loads from ~/.debriefeur/.env or environment variables.

Like Hermes uses ~/.hermes/ and OpenClaw uses ~/.openclaw/,
Debriefeur stores config in ~/.debriefeur/.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def get_debrief_home() -> Path:
    """Return the debrief home directory (~/.debriefeur)."""
    home = Path(os.environ.get("DEBRIEF_HOME", Path.home() / ".debriefeur"))
    home.mkdir(parents=True, exist_ok=True)
    return home


def get_sessions_dir() -> Path:
    """Return the sessions storage directory."""
    d = get_debrief_home() / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_output_dir() -> Path:
    """Return the default output directory for generated configs."""
    d = get_debrief_home() / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_config() -> dict:
    """Load configuration from environment and ~/.debriefeur/.env."""
    env_path = get_debrief_home() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # Also load from current directory .env (lower priority)
    load_dotenv(override=False)

    return {
        # Model tiers — litellm naming convention
        "model_tier_fast": os.environ.get(
            "MODEL_TIER_FAST", "openrouter/qwen/qwen3.5-397b-a17b"
        ),
        "model_tier_deep": os.environ.get(
            "MODEL_TIER_DEEP", "openrouter/moonshotai/kimi-k2.5"
        ),
        "model_tier_synthesis": os.environ.get(
            "MODEL_TIER_SYNTHESIS", "openrouter/z-ai/glm-5"
        ),
    }
