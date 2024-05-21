from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer

from settings import settings


def embedd_text(text: str):
    model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    return model.encode(text)


def embedd_repositories(text: str):
    model = INSTRUCTOR("hkunlp/instructor-xl")
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])
