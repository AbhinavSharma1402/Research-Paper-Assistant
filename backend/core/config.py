import os
from pathlib import Path
from pydantic import BaseSettings, AnyUrl

BASE_DIR = Path(__file__).resolve().parent.parent


def get_env_path():
    env_path = BASE_DIR.parent / ".env"
    return env_path


class Settings(BaseSettings):
    app_name: str = "Research Paper Assistant"
    api_prefix: str = "/api"
    secret_key: str = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR.parent / 'data' / 'app.db'}")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    vector_store_root: str = os.getenv("VECTOR_STORE_ROOT", str(BASE_DIR.parent / "vectorstore"))
    upload_dir: str = os.getenv("UPLOAD_DIR", str(BASE_DIR.parent / "uploads"))
    max_upload_files: int = 20
    max_pdf_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200
    query_top_k: int = 5
    cache_ttl_seconds: int = 1800
    postgres_schema: str = "public"

    class Config:
        env_file = get_env_path()
        env_file_encoding = "utf-8"


settings = Settings()
