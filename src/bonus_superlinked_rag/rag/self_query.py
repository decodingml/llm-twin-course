from llm.chain import GeneralChain
from llm.llm_provider import get_chat_model
from llm.prompt_templates import SelfQueryTemplate


class SelfQuery:
    @staticmethod
    def generate_response(query: str) -> str | None:
        prompt = SelfQueryTemplate().create_template()
        model = get_chat_model(temperature=0)

        chain = GeneralChain().get_chain(
            llm=model, output_key="metadata_filter_value", template=prompt
        )

        response = chain.invoke({"question": query})
        result = response.get("metadata_filter_value", "none")
        
        if result.lower() == "none":
            return None

        return result
