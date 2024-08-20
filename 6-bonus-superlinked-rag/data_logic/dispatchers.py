from data_logic.cleaning_data_handlers import (
    ArticleCleaningHandler,
    CleaningDataHandler,
    PostCleaningHandler,
    RepositoryCleaningHandler,
)
from models.documents import Document
from models.raw import ArticleRawModel, PostsRawModel, RawModel, RepositoryRawModel
from utils.logging import get_logger

logger = get_logger(__name__)


class RawDispatcher:
    @staticmethod
    def handle_mq_message(message: dict) -> RawModel:
        data_type = message.get("type")

        logger.info("Received raw message.", data_type=data_type)

        if data_type == "posts":
            return PostsRawModel(**message)
        elif data_type == "articles":
            return ArticleRawModel(**message)
        elif data_type == "repositories":
            return RepositoryRawModel(**message)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")


class CleaningHandlerFactory:
    @staticmethod
    def create_handler(data_type: str) -> CleaningDataHandler:
        if data_type == "posts":
            return PostCleaningHandler()
        elif data_type == "articles":
            return ArticleCleaningHandler()
        elif data_type == "repositories":
            return RepositoryCleaningHandler()
        else:
            raise ValueError("Unsupported data type")


class CleaningDispatcher:
    cleaning_factory = CleaningHandlerFactory()

    @classmethod
    def dispatch_cleaner(cls, data_model: RawModel) -> list[Document]:
        logger.info("Cleaning data.", data_type=data_model.type)

        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        cleaned_models = handler.clean(data_model)

        logger.info(
            "Data cleaned successfully.",
            data_type=data_type,
            len_cleaned_documents=len(cleaned_models),
            len_content=sum([len(doc.content) for doc in cleaned_models]),
        )

        return cleaned_models
