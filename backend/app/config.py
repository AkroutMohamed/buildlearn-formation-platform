import os
from pathlib import Path


def _env(key: str, default: str = "") -> str:
    """Read an environment variable, accepting both upper and lower case names.

    The previous pydantic-based settings resolved fields case-insensitively, so
    both ``CORS_ORIGINS`` and ``cors_origins`` are honoured here.
    """
    return os.environ.get(key) or os.environ.get(key.lower()) or os.environ.get(key.upper()) or default


def _require_env(key: str) -> str:
    """Read a required environment variable, accepting both upper and lower case names.

    Raises ``RuntimeError`` if the variable is not set.
    """
    value = os.environ.get(key) or os.environ.get(key.lower()) or os.environ.get(key.upper())
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def _load_dotenv(path: Path) -> None:
    """Minimal ``.env`` loader (KEY=VALUE lines) so environment files still work."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class Settings:
    def __init__(self) -> None:
        _load_dotenv(Path(".env"))
        self.app_name: str = _env("app_name", "Formation Platform")
        self.debug: bool = _env("debug", "false").lower() in {"1", "true", "yes", "on"}
        self.database_url: str = _require_env("DATABASE_URL")
        self.cors_origins: str = _env(
            "cors_origins", "http://localhost:3000,http://127.0.0.1:3000"
        )
        self.upload_dir: str = _env("upload_dir", "uploads")
        self.jwt_secret_key: str = _require_env("JWT_SECRET_KEY")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir).resolve()


settings = Settings()
