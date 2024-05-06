import json
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from comet_ml import Artifact, Experiment

from db.qdrant import connection as client
from finetuning.file_handler import FileHandler
from finetuning.llm_communication import GptCommunicator
from settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

data_type = "posts"
USER_PROMPT = (
    f"In the following rows I will give you 2 json objects as example, each of them having an instruction which "
    f"describes what to write about and the corresponding {data_type} content that follows this instruction. Afterwards I "
    f"will give you batches of other contents of {data_type} and please generate me one instruction for each of them. The {data_type} text "
    f"for which you have to generate the instructions is under Content number x lines. Please structure them in json format,"
    f"ready to be loaded in json,a list of objects only with fields called instruction ( the generated part ) and content ( the provided part ). "
    f"Please do not add any extra characters!\n"
)


class DataFormatter:

    @classmethod
    def format_data(cls, data_points: list, is_example: bool) -> str:
        text = ""
        for index, data_point in enumerate(data_points):
            if not is_example:
                text += f"Content number {index + 1}\n"
            text += str(data_point) + "\n"
        return text

    @classmethod
    def format_batch(cls, context_msg: str, data_points: list) -> str:
        delimiter_msg = context_msg
        delimiter_msg += cls.format_data(data_points, False)
        return delimiter_msg

    @classmethod
    def format_initial_prompt(cls, example_content: list, inference_posts: list):
        initial_prompt = (
            USER_PROMPT  # Assuming USER_PROMPT is defined somewhere as a global constant or class attribute
        )
        initial_prompt += f"You must generate exactly a list of {len(inference_posts)} json objects, using the contents provided under CONTENTS FOR GENERATION, the EXAMPLE JSONS are just for example purpose.\n"
        initial_prompt += "EXAMPLE JSONS:\n"
        initial_prompt += cls.format_data(example_content, True)
        initial_prompt += cls.format_batch("CONTENTS FOR GENERATION: \n", inference_posts)
        return initial_prompt


class DatasetGenerator:
    def __init__(self, file_handler: FileHandler, api_communicator: GptCommunicator, data_formatter: DataFormatter):
        self.file_handler = file_handler
        self.api_communicator = api_communicator
        self.data_formatter = data_formatter

    def generate_training_data(self, example_file: str, collection_name: str, batch_size: int = 1):
        example_content = self.file_handler.read_json(example_file)
        all_contents = self.fetch_all_cleaned_content(collection_name)
        response = []
        for i in range(0, len(all_contents), batch_size):
            batch = all_contents[i : i + batch_size]
            initial_prompt = data_formatter.format_initial_prompt(example_content, batch)
            response += self.api_communicator.send_prompt(initial_prompt)

        self.push_to_comet(response, collection_name)

    def push_to_comet(self, data: list, collection_name: str):
        try:
            logging.info(f"Starting to push data to Comet: {collection_name}")

            # Assuming the settings module has been properly configured with the required attributes
            experiment = Experiment(
                api_key=settings.COMET_API_KEY, project_name=settings.COMET_PROJECT, workspace=settings.COMET_WORKSPACE
            )

            file_name = f"{collection_name}.json"
            logging.info(f"Writing data to file: {file_name}")

            with open(file_name, "w") as f:
                json.dump(data, f)

            logging.info("Data written to file successfully")

            artifact = Artifact(collection_name)
            artifact.add(file_name)
            logging.info(f"Artifact created and file added: {file_name}")

            experiment.log_artifact(artifact)
            experiment.end()
            logging.info("Data pushed to Comet successfully and experiment ended")

        except Exception as e:
            logging.error(f"Failed to push data to Comet: {e}", exc_info=True)

    def fetch_all_cleaned_content(self, collection_name: str) -> list:
        all_cleaned_contents = []

        scroll_response = client.scroll(collection_name=collection_name, limit=10000)
        points = scroll_response[0]

        for point in points:
            cleaned_content = point.payload["cleaned_content"]
            if cleaned_content:
                all_cleaned_contents.append(cleaned_content)

        return all_cleaned_contents


if __name__ == "__main__":
    filename = "example_content.json"
    relative_directory = "finetuning"
    example_file = Path(relative_directory) / filename
    collection_names = ["cleaned_articles", "cleaned_posts"]
    file_handler = FileHandler()
    api_communicator = GptCommunicator()
    data_formatter = DataFormatter()
    dataset_generator = DatasetGenerator(file_handler, api_communicator, data_formatter)
    for collection in collection_names:
        dataset_generator.generate_training_data(example_file=example_file, collection_name=collection, batch_size=1)
