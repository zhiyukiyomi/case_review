from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / ".env")


def _resolve_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


@dataclass(slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Test Coverage Evaluation Agent")
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    cors_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        ]
    )
    upload_dir: Path = field(
        default_factory=lambda: _resolve_path(os.getenv("UPLOAD_DIR", "runtime/uploads"), BACKEND_ROOT)
    )
    report_dir: Path = field(
        default_factory=lambda: _resolve_path(os.getenv("REPORT_DIR", "runtime/reports"), BACKEND_ROOT)
    )
    temp_dir: Path = field(
        default_factory=lambda: _resolve_path(os.getenv("TEMP_DIR", "runtime/tmp"), BACKEND_ROOT)
    )
    max_workers: int = int(os.getenv("MAX_WORKERS", "4"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "5000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "400"))
    llm_timeout: float = float(os.getenv("LLM_TIMEOUT", "120"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    llm_repair_retries: int = int(os.getenv("LLM_REPAIR_RETRIES", "1"))
    coverage_batch_size: int = int(os.getenv("COVERAGE_BATCH_SIZE", "12"))
    prompt_text_preview_chars: int = int(os.getenv("PROMPT_TEXT_PREVIEW_CHARS", "240"))
    demo_mode: bool = os.getenv("DEMO_MODE", "false").lower() == "true"
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def ensure_directories(self) -> None:
        for path in (self.upload_dir, self.report_dir, self.temp_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
