import sys
from pathlib import Path

# To mimic using multiple Python modules, such as 'core' and 'feature_pipeline',
# we will add the './src' directory to the PYTHONPATH. This is not intended for
# production use cases but for development and educational purposes.
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.append(ROOT_DIR)

from core.config import settings
from llm_twin import LLMTwin

settings.patch_localhost()


import gradio as gr
from inference_pipeline.llm_twin import LLMTwin

llm_twin = LLMTwin(mock=False)


def predict(message: str, history: list[list[str]], author: str) -> str:
    """
    Generates a response using the LLM Twin, simulating a conversation with your digital twin.

    Args:
        message (str): The user's input message or question.
        history (List[List[str]]): Previous conversation history between user and twin.
        about_me (str): Personal context about the user to help personalize responses.

    Returns:
        str: The LLM Twin's generated response.
    """

    query = f"I am {author}. Write about: {message}"
    response = llm_twin.generate(
        query=query, enable_rag=True, sample_for_evaluation=False
    )

    return response["answer"]


demo = gr.ChatInterface(
    predict,
    textbox=gr.Textbox(
        placeholder="Chat with your LLM Twin",
        label="Message",
        container=False,
        scale=7,
    ),
    additional_inputs=[
        gr.Textbox(
            "Paul Iusztin",
            label="Who are you?",
        )
    ],
    title="Your LLM Twin",
    description="""
    Chat with your personalized LLM Twin! This AI assistant will help you write content incorporating your style and voice.
    """,
    theme="soft",
    examples=[
        [
            "Draft a post about RAG systems.",
            "Paul Iusztin",
        ],
        [
            "Draft an article paragraph about vector databases.",
            "Paul Iusztin",
        ],
        [
            "Draft a post about LLM chatbots.",
            "Paul Iusztin",
        ],
    ],
    cache_examples=False,
)


if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=True)
