import json
import openai
from openai import OpenAI
from comet_ml import Experiment, Artifact
from qdrant_client import QdrantClient

HOST = "localhost"
PORT = 6333
MAX_LENGTH = 16384
LLM_API_KEY = ""
COMET_API_KEY = ""
COMET_WORKSPACE = "915-muscalagiu-ancaioana"
COMET_PROJECT = "scrabble"
SYSTEM_PROMPT = "You are a technical writer handing someone's account to post about AI and MLOps."
USER_PROMPT = "In the following rows I will give you 3 json objects, each of them having an instruction which " \
              "describes what to write about and the corresponding post that follows this instruction. Afterwards I " \
              "will give you batches of other posts and please generate me instructions for them. The posts text is " \
              "under Post number x lines. Please structure them in json format, ready to be loaded in json," \
              "a list of objects only with field called instruction and post. " \
              "Please do not add any extra characters!\n"


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
        f.write(str(data))
        f.close()

        artifact = Artifact(collection_name)
        artifact.add(file_name)

        experiment.log_artifact(artifact)
        experiment.end()

    @staticmethod
    def format_example_data(data_points: list):
        index = 0
        text = ""
        for data_point in data_points:
            text += "Post number " + str(index) + "\n"
            text += str(data_point)
            text += '\n'
            index += 1
        return text

    @staticmethod
    def format_batch(context_msg: str, data_points: list) -> str:
        delimiter_msg = context_msg
        delimiter_msg += DatasetGenerator.format_example_data(data_points)
        return delimiter_msg

    @staticmethod
    def format_initial_prompt(example_posts: list, inference_posts: list):
        initial_prompt = USER_PROMPT
        initial_prompt += DatasetGenerator.format_example_data(example_posts)
        initial_prompt += DatasetGenerator.format_batch("Batch of other posts: \n", inference_posts)
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
    def generate_training_data(example_file: str, collection_name: str, batch_size: int = 5):
        response = []
        example_posts = DatasetGenerator.parse_json_file(example_file)
        all_posts = DatasetGenerator.fetch_all_cleaned_content(collection_name)
        batch = all_posts[0:batch_size]
        prompt = DatasetGenerator.format_initial_prompt(example_posts, batch)
        response += DatasetGenerator.send_prompt_to_llm(prompt)
        for i in range(batch_size, len(all_posts), batch_size):
            batch = all_posts[i:i + batch_size]
            batch_msg = DatasetGenerator.format_initial_prompt(example_posts, batch)
            response += DatasetGenerator.send_prompt_to_llm(batch_msg)

        for i in range(len(response)):
            response[i]["post"] = all_posts[i]
        DatasetGenerator.push_to_comet(response, collection_name)


example_file = "example_posts.json"
collection_name = "cleaned_articles"
DatasetGenerator.generate_training_data(example_file, collection_name, 6)
