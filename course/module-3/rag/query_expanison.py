from langchain_openai import ChatOpenAI

from llm_components.chain import GeneralChain
from llm_components.prompt_templates import QueryExpansionTemplate
from settings import settings


class QueryExpansion:
    @staticmethod
    def generate_response(query: str) -> list[str]:
        prompt = QueryExpansionTemplate(question=query).create_template()
        model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, temperature=0)

        chain = GeneralChain().get_chain(
            llm=model, output_key="expanded_queries", template=prompt
        )

        response = chain.invoke({"question": query})
        result = response["expanded_queries"]
        queries = result.strip().split("\n")
        cleaned_queries = [item.strip() for item in queries if item.strip()]
        return cleaned_queries
