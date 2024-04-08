from abc import ABC, abstractmethod
from pydantic import BaseModel
from qdrant_client.models import Batch


class DataModel(ABC, BaseModel):
    """
    Abstract class for all data model
    """
    entry_id: int
    type: str


class DBDataModel(DataModel):
    """
    Abstract class for all data models that need to be saved into a vector DB (e.g. Qdrant)
    """
    entry_id: int
    type: str

    @abstractmethod
    def save(self):
        pass
