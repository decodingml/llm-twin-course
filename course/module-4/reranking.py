from rag.rag_clients.llm_components.prompt_templates import RerankingTemplate
from rag.rag_clients.llm_components.chain import GeneralChain
from langchain_openai import ChatOpenAI


class Reranker:

    @staticmethod
    def generate_response(query: str, passages: str) -> list[str]:
        prompt = RerankingTemplate(question=query, passages=passages).create_template()
        model = ChatOpenAI(model='gpt-4-1106-preview')
        chain = GeneralChain().get_chain(llm=model, output_key='rerank', template=prompt)

        response = chain.invoke({'question': query, 'passages': passages})
        result = response['rerank']

        return result
