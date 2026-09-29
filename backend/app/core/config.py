import warnings
from urllib.parse import urlparse
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Keys that must never be used to sign JWTs in production. The first was the old
# hardcoded default committed to source; an attacker who knows it can forge tokens.
_WEAK_SECRET_KEYS = {"", "change-me-please", "45646548789wefds5f4s6d5f4sdf"}
_DEV_ENVS = {"development", "dev", "local", "test", "testing"}

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "NetworkManager"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # No secure default: a strong SECRET_KEY must be provided via the environment.
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    JWT_ALGORITHM: str = "HS256"

    # Comma-separated origins
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/network_manager"

    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    # Optional initial admin seeding (for development/bootstrap)
    ADMIN_USERNAME: str | None = None
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    # Background jobs
    BACKGROUND_JOBS_ENABLED: bool = True
    OPERATIONS_POLL_INTERVAL_SEC: int = 5
    NOTIFICATIONS_POLL_INTERVAL_SEC: int = 5
    OPERATION_TIMEOUT_SEC: int = 30
    MAX_OPERATION_RETRIES: int = 2
    OPERATION_RETRY_BACKOFF_BASE_SEC: int = 2

    # API Security and limits
    ENABLE_RATE_LIMIT: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120
    ENABLE_IP_ALLOWLIST: bool = False
    API_ALLOWED_IPS: str = ""  # comma-separated list; empty disables
    MAX_REQUEST_BODY_BYTES: int = 1_000_000  # 1 MB
    API_KEYS: str = ""  # comma-separated API keys for agent/ingestion
    REQUEST_ID_HEADER: str = "X-Request-ID"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _ensure_postgres_asyncpg(cls, v: str) -> str:
        if not v:
            return v
        # Accept both postgresql+asyncpg:// and postgresql:// (normalize to asyncpg)
        if v.startswith("postgresql+asyncpg://"):
            return v
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Reject any non-PostgreSQL URL
        scheme = urlparse(v).scheme
        raise ValueError(f"Unsupported DATABASE_URL scheme '{scheme}'. Use 'postgresql+asyncpg://'")

    @model_validator(mode="after")
    def _validate_secret_key(self) -> "Settings":
        key = (self.SECRET_KEY or "").strip()
        weak = (
            key in _WEAK_SECRET_KEYS
            or (key.startswith("<") and key.endswith(">"))  # unreplaced placeholder
            or len(key) < 16
        )
        if weak:
            msg = (
                "SECRET_KEY is unset, a placeholder, or too weak. JWTs signed with a "
                "predictable key can be forged (full auth/RBAC bypass). Set a strong "
                'random value, e.g. `python -c "import secrets; print(secrets.token_urlsafe(48))"`.'
            )
            if self.APP_ENV.lower() not in _DEV_ENVS:
                raise ValueError(msg)
            warnings.warn(msg, stacklevel=2)
        return self


settings = Settings()
