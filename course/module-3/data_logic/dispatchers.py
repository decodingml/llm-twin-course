from data_logic.chunking_data_handlers import (
    ArticleChunkingHandler,
    ChunkingDataHandler,
    PostChunkingHandler,
    RepositoryChunkingHandler,
)
from data_logic.cleaning_data_handlers import (
    ArticleCleaningHandler,
    CleaningDataHandler,
    PostCleaningHandler,
    RepositoryCleaningHandler,
)
from data_logic.embedding_data_handlers import (
    ArticleEmbeddingHandler,
    EmbeddingDataHandler,
    PostEmbeddingHandler,
    RepositoryEmbeddingHandler,
)
from models.base import DataModel
from models.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel


class RawDispatcher:

    @staticmethod
    def handle_mq_message(message: dict) -> DataModel:
        data_type = message.get("type")
        if data_type == "posts":
            return PostsRawModel(**message)
        elif data_type == "articles":
            return ArticleRawModel(**message)
        elif data_type == "repositories":
            return RepositoryRawModel(**message)
        else:
            raise ValueError("Unsupported data type")


class CleaningHandlerFactory:

    @staticmethod
    def create_handler(data_type) -> CleaningDataHandler:
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
    def dispatch_cleaner(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        clean_model = handler.clean(data_model)
        return clean_model


class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> ChunkingDataHandler:
        if data_type == "posts":
            return PostChunkingHandler()
        elif data_type == "articles":
            return ArticleChunkingHandler()
        elif data_type == "repositories":
            return RepositoryChunkingHandler()
        else:
            raise ValueError("Unsupported data type")


class ChunkingDispatcher:
    cleaning_factory = ChunkingHandlerFactory

    @classmethod
    def dispatch_chunker(cls, data_model: DataModel) -> list[DataModel]:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        chunk_models = handler.chunk(data_model)
        return chunk_models


class EmbeddingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> EmbeddingDataHandler:
        if data_type == "posts":
            return PostEmbeddingHandler()
        elif data_type == "articles":
            return ArticleEmbeddingHandler()
        elif data_type == "repositories":
            return RepositoryEmbeddingHandler()
        else:
            raise ValueError("Unsupported data type")


class EmbeddingDispatcher:
    cleaning_factory = EmbeddingHandlerFactory

    @classmethod
    def dispatch_embedder(cls, data_model: DataModel) -> DataModel:
        data_type = data_model.type
        handler = cls.cleaning_factory.create_handler(data_type)
        embedded_chunk_model = handler.embedd(data_model)
        return embedded_chunk_model
