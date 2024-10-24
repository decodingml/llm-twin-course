import core.logger_utils as logger_utils
import opik
from core import lib
from core.db.documents import UserDocument
from langchain_openai import ChatOpenAI

from config import settings
from llm.prompt_templates import SelfQueryTemplate

logger = logger_utils.get_logger(__name__)


class SelfQuery:
    @staticmethod
    @opik.track(name="SelQuery.generate_response")
    def generate_response(query: str) -> str | None:
        prompt = SelfQueryTemplate().create_template()
        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

        chain = prompt | model

        response = chain.invoke({"question": query})
        user_full_name = response.content.strip("\n ")

        if user_full_name == "none":
            return None

        logger.info(
            f"Successfully extracted the user full name from the query.",
            user_full_name=user_full_name,
        )
        first_name, last_name = lib.split_user_full_name(user_full_name)
        logger.info(
            f"Successfully extracted the user first and last name from the query.",
            user_full_name=first_name,
            last_name=last_name,
        )
        user_id = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

        return user_id
