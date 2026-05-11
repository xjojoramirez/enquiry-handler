import os
from pathlib import Path

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

        self._config_data = self._load_config()
        self.classification_types: list[str] = self._config_data.get(
            "classification_types",
            ["new_client", "support_request", "complaint", "general_question"],
        )
        self.webhook_url: str = self._config_data.get("webhook_url", "")
        self.system_prompt: str = self._config_data.get(
            "system_prompt",
            "You are an AI assistant for Strata Management Consultants.",
        )

    def _load_config(self) -> dict:
        path = Path(CONFIG_PATH)
        if not path.exists():
            return {}
        try:
            with open(path) as f:
                result = yaml.safe_load(f)
                return result if isinstance(result, dict) else {}
        except yaml.YAMLError:
            return {}

    def model_config(self) -> dict:
        return self._config_data.get("model", {})


settings = Settings()
