import model_evaluation.evaluation as eval
from dotenv import load_dotenv
from inference import ModelInference
from model_evaluation.prompt_monitor import PromptMonitor

if __name__ == "__main__":
    load_dotenv()
    tool = ModelInference()
    llm_monitor = PromptMonitor()
    query = """Could you please draft a LinkedIn post discussing Vector Databases? I'm particularly interested in how do they work."""
    [content] = tool.infer_only(query=query)["content"]

    result = eval.llm_eval_using_GPT(query=query, output=content)
    print(result)
    llm_monitor.log_prompt(
        prompt=result, prompt_template_variables={"query": query}, output=content
    )

    for item in content:
        print(item)
