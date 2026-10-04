from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigLoader:

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)

    def load(self) -> Dict[str, Any]:

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            config = yaml.safe_load(file)

        if not config:
            raise ValueError(
                "Configuration file is empty."
            )

        return config