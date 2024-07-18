import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class OpenApiDescriptionUtil:
    @staticmethod
    def get_open_api_description_by_key(key: str, file_path: str | None = None) -> dict[str, Any]:
        if file_path is None:
            file_path = os.path.join(os.getcwd(), "executor/openapi/static_endpoint_descriptor.json")
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
            open_api_description = data.get(key)
            if open_api_description is None:
                logger.warning("No OpenAPI description found for key: %s", key)
            return open_api_description
