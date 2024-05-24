from langchain_openai import ChatOpenAI
from llm_components.chain import GeneralChain
from llm_components.prompt_templates import SelfQueryTemplate
from settings import settings


class SelfQuery:
    @staticmethod
    def generate_response(query: str) -> str:
        prompt = SelfQueryTemplate().create_template()
        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

        chain = GeneralChain().get_chain(
            llm=model, output_key="metadata_filter_value", template=prompt
        )

        response = chain.invoke({"question": query})
        result = response["metadata_filter_value"]

        return result
