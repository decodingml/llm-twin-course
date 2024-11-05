import opik
from config import settings
from langchain_openai import ChatOpenAI
from core.rag.prompt_templates import QueryExpansionTemplate
from opik.integrations.langchain import OpikTracer


class QueryExpansion:
    opik_tracer = OpikTracer(tags=["QueryExpansion"])

    @staticmethod
    @opik.track(name="QueryExpansion.generate_response")
    def generate_response(query: str, to_expand_to_n: int) -> list[str]:
        query_expansion_template = QueryExpansionTemplate()
        prompt = query_expansion_template.create_template(to_expand_to_n)
        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
        chain = prompt | model
        chain = chain.with_config({"callbacks": [QueryExpansion.opik_tracer]})

        response = chain.invoke({"question": query})
        response = response.content

        queries = response.strip().split(query_expansion_template.separator)
        stripped_queries = [
            stripped_item for item in queries if (stripped_item := item.strip(" \\n"))
        ]

        return stripped_queries
