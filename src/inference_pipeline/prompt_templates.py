from core.rag.prompt_templates import BasePromptTemplate
from langchain.prompts import PromptTemplate


class InferenceTemplate(BasePromptTemplate):
    simple_system_prompt: str = """
    You are an AI language model assistant. Your task is to generate a cohesive and concise response based on the user's instruction by using a similar writing style and voice.
"""
    simple_prompt_template: str = """
### Instruction:
{question}
"""

    rag_system_prompt: str = """ You are a specialist in technical content writing. Your task is to create technical content based on the user's instruction given a specific context 
with additional information consisting of the user's previous writings and his knowledge.

Here is a list of steps that you need to follow in order to solve this task:

Step 1: You need to analyze the user's instruction.
Step 2: You need to analyze the provided context and how the information in it relates to the user instruction.
Step 3: Generate the content keeping in mind that it needs to be as cohesive and concise as possible based on the query. You will use the users writing style and voice inferred from the user instruction and context.
First try to answer based on the context. If the context is irrelevant answer with "I cannot answer your question, as I don't have enough context."
"""
    rag_prompt_template: str = """
### Instruction:
{question}

### Context:
{context}
"""

    def create_template(self, enable_rag: bool = True) -> tuple[str, PromptTemplate]:
        if enable_rag is True:
            return self.rag_system_prompt, PromptTemplate(
                template=self.rag_prompt_template,
                input_variables=["question", "context"],
            )

        return self.simple_system_prompt, PromptTemplate(
            template=self.simple_prompt_template, input_variables=["question"]
        )
