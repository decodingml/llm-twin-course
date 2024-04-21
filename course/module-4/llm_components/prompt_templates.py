from abc import ABC, abstractmethod
from langchain.prompts import PromptTemplate
from pydantic import BaseModel


class BasePromptTemplate(ABC, BaseModel):

    @abstractmethod
    def create_template(self) -> PromptTemplate:
        pass


class QueryExpansionTemplate(BasePromptTemplate):

    prompt: str = """You are an AI language model assistant. Your task is to generate Five
    different versions of the given user question to retrieve relevant documents from a vector
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these alternative questions seperated by newlines.
    Original question: {question}"""

    question: str

    def create_template(self) -> PromptTemplate:
        template = PromptTemplate(template=self.prompt, input_variables=['question'], verbose=True)
        template.format(question=self.question)
        return template


class SelfQueryTemplate(BasePromptTemplate):

    prompt: str = """You are an AI language model assistant. Your task is to extract information from a user question.
    The required information that needs to be extracted is the user id. 
    Your response should consists of only the extracted id (e.g. 1345256), nothing else.
    User question: {question}"""

    question: str

    def create_template(self) -> PromptTemplate:
        template = PromptTemplate(template=self.prompt, input_variables=['question'], verbose=True)
        template.format(question=self.question)
        return template


class RerankingTemplate(BasePromptTemplate):
    prompt: str = """You are an AI language model assistant. Your task is to rerank passages related to a query
    based on their relevance. The most relevant passages should be put at the beginning and at the end. 
    You should only pick at max 5 passages.
    The following are passages related to this query: {question}.
    Passages: {passages}
    """

    question: str

    passages: str

    def create_template(self) -> PromptTemplate:
        template = PromptTemplate(template=self.prompt, input_variables=['question', 'passages'], verbose=True)
        template.format(question=self.question, passages=self.passages)
        return template
