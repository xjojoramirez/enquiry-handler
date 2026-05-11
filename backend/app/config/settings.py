import os
from pathlib import Path
from typing import Optional

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


class Settings:
    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://enquiries:enquiries@localhost:5432/enquiries",
        )
        self.api_key: str = os.getenv("API_KEY", "")
        self.model_name: str = os.getenv("MODEL_NAME", "deepseek-v4-flash")
        self.model_base_url: str = os.getenv(
            "MODEL_BASE_URL", "https://api.opencode.ai/v1"
        )

        raw = self._load_config()
        self.classification_types: list[str] = raw.get(
            "classification_types",
            ["new_client", "support_request", "complaint", "general_question"],
        )
        self.webhook_url: str = raw.get("webhook_url", "")
        self.system_prompt: str = raw.get(
            "system_prompt",
            "You are an AI assistant for Strata Management Consultants.",
        )

    def _load_config(self) -> dict:
        path = Path(CONFIG_PATH)
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def model_config(self) -> dict:
        raw = self._load_config()
        return raw.get("model", {})


settings = Settings()
