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
        types_str = "|".join(self.classification_types)
        self.system_prompt: str = self._config_data.get(
            "system_prompt",
            f"""You are an AI assistant for Strata Business Brokers.
Analyse the client enquiry and return a JSON object with:
- classification: object with type ({types_str}), subtype (string), confidence (0.0-1.0), explanation (string)
- priority: low|medium|high
- summary: one-sentence summary
- entities: object with extracted names, unit numbers, etc.
- recommended_team: string
- suggested_response: draft reply text

Think step by step before answering. Output valid JSON only.""",
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
