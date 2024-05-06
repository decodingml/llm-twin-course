import json
import openai
from openai import OpenAI
from comet_ml import Experiment, Artifact
from qdrant_client import QdrantClient

example_file = "example_content.json"
collection_name = "cleaned_posts"
data_type = "articles"
HOST = "localhost"
PORT = 6333
MAX_LENGTH = 16384
LLM_API_KEY = ""
COMET_API_KEY = ""
COMET_WORKSPACE = "915-muscalagiu-ancaioana"
COMET_PROJECT = "scrabble"
SYSTEM_PROMPT = "You are a technical writer handing someone's account to post about AI and MLOps."
USER_PROMPT = (
    f'In the following rows I will give you 2 json objects as example, each of them having an instruction which '
    f'describes what to write about and the corresponding {data_type} content that follows this instruction. Afterwards I '
    f'will give you batches of other contents of {data_type} and please generate me one instruction for each of them. The {data_type} text '
    f'for which you have to generate the instructions is under Content number x lines. Please structure them in json format,'
    f'ready to be loaded in json,a list of objects only with fields called instruction ( the generated part ) and content ( the provided part ). '
    f'Please do not add any extra characters!\n'
)


class DatasetGenerator:
    @staticmethod
    def clean_response(response: str) -> str:
        start_index = response.find('[')
        end_index = response.rfind(']')
        return response[start_index:end_index + 1]

    @staticmethod
    def parse_json_file(filename: str) -> list:
        try:
            with open(filename, 'r') as file:
                json_objects = json.load(file)
                return json_objects
        except FileNotFoundError:
            print(f"Error: The file '{filename}' does not exist.")
            return []
        except json.JSONDecodeError:
            print(f"Error: The file '{filename}' is not properly formatted as JSON.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    @staticmethod
    def send_prompt_to_llm(prompt: str) -> list:
        openai.api_key = LLM_API_KEY
        try:
            client = OpenAI(
                api_key=LLM_API_KEY,
            )
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt[:MAX_LENGTH],
                    }
                ],
                model="gpt-3.5-turbo",
            )
            response = chat_completion.choices[0].message.content
            response = DatasetGenerator.clean_response(response)

            response_json_list = json.loads(response)

            return response_json_list

        except Exception as e:
            print(f"An error occurred, skipping batch: {e}")
            return []

    @staticmethod
    def push_to_comet(data: list, collection_name: str):
        experiment = Experiment(
            api_key=COMET_API_KEY,
            project_name=COMET_PROJECT,
            workspace=COMET_WORKSPACE
        )
        file_name = f'{collection_name}.json'
        f = open(file_name, "w")
        json.dump(data, f)
        f.close()

        artifact = Artifact(collection_name)
        artifact.add(file_name)

        experiment.log_artifact(artifact)
        experiment.end()

    @staticmethod
    def format_data(data_points: list, is_example: bool):
        index = 0
        text = ""
        for data_point in data_points:
            if not is_example:
                text += "Content number " + str(index + 1) + "\n"
            text += str(data_point)
            text += '\n'
            index += 1
        return text

    @staticmethod
    def format_batch(context_msg: str, data_points: list) -> str:
        delimiter_msg = context_msg
        delimiter_msg += DatasetGenerator.format_data(data_points, False)
        return delimiter_msg

    @staticmethod
    def format_initial_prompt(example_content: list, inference_posts: list):
        initial_prompt = USER_PROMPT
        initial_prompt += f'You must generate exactly a list of {len(inference_posts)} json objects, using the contents provided under CONTENTS FOR GENERATION, the EXAMPLE JSONS are just for example purpose.\n'
        initial_prompt += 'EXAMPLE JSONS:\n'
        initial_prompt += DatasetGenerator.format_data(example_content, True)
        initial_prompt += DatasetGenerator.format_batch("CONTENTS FOR GENERATION: \n", inference_posts)
        return initial_prompt

    @staticmethod
    def fetch_all_cleaned_content(collection_name: str) -> list:
        client = QdrantClient(host=HOST, port=PORT)
        all_cleaned_contents = []

        scroll_response = client.scroll(
            collection_name=collection_name,
            limit=10000
        )
        points = scroll_response[0]

        for point in points:
            cleaned_content = point.payload['cleaned_content']
            if cleaned_content:
                all_cleaned_contents.append(cleaned_content)

        return all_cleaned_contents

    @staticmethod
    def generate_training_data(example_file: str, collection_name: str, batch_size: int = 1):
        response = []
        example_content = DatasetGenerator.parse_json_file(example_file)
        all_contents = DatasetGenerator.fetch_all_cleaned_content(collection_name)
        batch = all_contents[0:batch_size]
        prompt = DatasetGenerator.format_initial_prompt(example_content, batch)
        response += DatasetGenerator.send_prompt_to_llm(prompt)
        for i in range(batch_size, len(all_contents), batch_size):
            batch = all_contents[i:i + batch_size]
            batch_msg = DatasetGenerator.format_initial_prompt(example_content, batch)
            response += DatasetGenerator.send_prompt_to_llm(batch_msg)

        for i in range(len(response)):
            response[i]["content"] = all_contents[i]
        DatasetGenerator.push_to_comet(response, collection_name)


DatasetGenerator.generate_training_data(example_file, collection_name, 1)
