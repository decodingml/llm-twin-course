import hashlib
import os
from enum import Enum

from executor.app.configuration.app_config import AppConfig


class HashType(Enum):
    MD5 = hashlib.md5


class FileHandlerService:
    def __init__(self, app_config: AppConfig, hash_type: HashType | None = None) -> None:
        self.__hash_type = hash_type or HashType.MD5
        self.app_config = app_config

    def generate_filename(self, field_id: str, app_id: str) -> str:
        filename = self.__hash_type.value(f"{app_id}_{field_id}".encode()).hexdigest()
        return f"{self.app_config.PERSISTENCE_FOLDER_PATH}/{filename}.json"

    def ensure_folder(self) -> None:
        os.makedirs(self.app_config.PERSISTENCE_FOLDER_PATH, exist_ok=True)
