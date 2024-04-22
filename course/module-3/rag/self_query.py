from langchain_openai import ChatOpenAI

from llm_components.chain import GeneralChain
from llm_components.prompt_templates import SelfQueryTemplate


class SelfQuery:

    @staticmethod
    def generate_response(query) -> str:
        prompt = SelfQueryTemplate(question=query).create_template()
        model = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)

        chain = GeneralChain().get_chain(llm=model, output_key="metadata_filter_value", template=prompt)

        response = chain.invoke(query)
        result = response["metadata_filter_value"]
        return result
