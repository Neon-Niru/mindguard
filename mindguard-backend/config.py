import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"


def _database_uri():
    url = (os.getenv("DATABASE_URL") or "").strip()

    if url:
        # Render/Heroku expose postgres:// but SQLAlchemy requires postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    return "sqlite:///" + str(INSTANCE_DIR / "mindguard.db")


# Origins the browser UI is served from. These are always allowed because the
# deployed frontend is a static site on a different origin from the API; without
# them every request fails the browser CORS preflight.
DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://neon-niru.github.io",
)


def _cors_origins():
    raw = (os.getenv("CORS_ORIGINS") or "").strip()

    # "*" disables origin restrictions (useful for throwaway previews).
    if raw == "*":
        return "*"

    # CORS_ORIGINS is additive: extra environments (a custom domain, a preview
    # deployment) can be listed without dropping the built-in origins.
    origins = list(DEFAULT_CORS_ORIGINS)

    for origin in raw.split(","):
        origin = origin.strip().rstrip("/")
        if origin and origin not in origins:
            origins.append(origin)

    return origins


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "mindguard-dev-secret-change-me",
    )

    SQLALCHEMY_DATABASE_URI = _database_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_EXPIRES_DAYS = int(os.getenv("JWT_EXPIRES_DAYS", "30"))

    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    CORS_ORIGINS = _cors_origins()

    # No SMTP provider is configured for the hackathon deployment. When this
    # is enabled, /api/forgot-password returns the reset token so the demo can
    # complete the reset flow without email delivery.
    RETURN_RESET_TOKEN = (
        os.getenv("RETURN_RESET_TOKEN", "false").lower() in ("1", "true", "yes")
    )

    JSON_SORT_KEYS = False
