"""
Settings for local development, Render, and Vercel-connected APIs.
"""
import os
from typing import List, Optional

try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
except Exception:
    def load_env():
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())
    load_env()


def _split_origins(raw: str) -> List[str]:
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts or ["*"]


class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "hackfest-secret-change-in-production")

    environment: str = os.getenv("ENVIRONMENT", os.getenv("RENDER", "") and "production" or "development")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("PORT") or os.getenv("API_PORT", "8000"))
    cors_origins: List[str] = _split_origins(os.getenv("CORS_ORIGINS", "*"))
    use_mock_db: bool = os.getenv("USE_MOCK_DB", "").lower() in ("1", "true", "yes")


settings = Settings()
