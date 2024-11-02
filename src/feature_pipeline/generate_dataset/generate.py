import json
import logging
from pathlib import Path

from comet_ml import Artifact, Experiment
from config import settings
from db import QdrantDatabaseConnector
from sklearn.model_selection import train_test_split
from utils.logging import get_logger

from .chunk_documents import chunk_documents
from .file_handler import FileHandler
from .llm_communication import GptCommunicator

logger = get_logger(__name__)


client = QdrantDatabaseConnector()


class DataFormatter:
    @classmethod
    def get_system_prompt(cls, data_type: str) -> str:
        return (
            f"I will give you batches of contents of {data_type}. Please generate me exactly 1 instruction for each of them. The {data_type} text "
            f"for which you have to generate the instructions is under Content number x lines. Please structure the answer in json format,"
            f"ready to be loaded by json.loads(), a list of objects only with fields called instruction and content. For the content field, copy the number of the content only!."
            f"Please do not add any extra characters and make sure it is a list with objects in valid json format!\n"
        )

    @classmethod
    def format_data(cls, data_points: list, is_example: bool, start_index: int) -> str:
        text = ""
        for index, data_point in enumerate(data_points):
            if not is_example:
                text += f"Content number {start_index + index }\n"
            text += str(data_point) + "\n"

        return text

    @classmethod
    def format_batch(cls, context_msg: str, data_points: list, start_index: int) -> str:
        delimiter_msg = context_msg
        delimiter_msg += cls.format_data(data_points, False, start_index)

        return delimiter_msg

    @classmethod
    def format_prompt(
        cls, inference_posts: list, data_type: str, start_index: int
    ) -> str:
        initial_prompt = cls.get_system_prompt(data_type)
        initial_prompt += f"You must generate exactly a list of {len(inference_posts)} json objects, using the contents provided under CONTENTS FOR GENERATION\n"
        initial_prompt += cls.format_batch(
            "\nCONTENTS FOR GENERATION: \n", inference_posts, start_index
        )

        return initial_prompt


class DatasetGenerator:
    def __init__(
        self,
        file_handler: FileHandler,
        api_communicator: GptCommunicator,
        data_formatter: DataFormatter,
    ):
        self.file_handler = file_handler
        self.api_communicator = api_communicator
        self.data_formatter = data_formatter

    def generate_training_data(
        self, collection_name: str, data_type: str, batch_size: int = 3
    ) -> None:
        cleaned_documents = self.fetch_all_cleaned_content(collection_name)
        cleaned_documents = chunk_documents(cleaned_documents)
        num_cleaned_documents = len(cleaned_documents)

        generated_instruct_dataset = []
        for i in range(0, num_cleaned_documents, batch_size):
            batch = cleaned_documents[i : i + batch_size]
            prompt = data_formatter.format_prompt(batch, data_type, i)
            generated_instruct_dataset += self.api_communicator.send_prompt(prompt)
            for j in range(i, min(i + batch_size, num_cleaned_documents)):
                generated_instruct_dataset[j]["content"] = cleaned_documents[j]

        train_test_split = self._split_dataset(generated_instruct_dataset)

        self.push_to_comet(train_test_split, data_type, collection_name)

    def _split_dataset(
        self, generated_instruct_dataset: list[dict], test_size: float = 0.1
    ) -> tuple[list[dict], list[dict]]:
        """Split dataset into train and test sets.

        Args:
            generated_instruct_dataset (dict): Dataset containing content and instruction pairs

        Returns:
            tuple[dict, dict]: Train and test splits of the dataset
        """

        if len(generated_instruct_dataset) == 0:
            return [], []

        train_data, test_data = train_test_split(
            generated_instruct_dataset, test_size=test_size, random_state=42
        )

        return train_data, test_data

    def push_to_comet(
        self,
        train_test_split: tuple[list[dict], list[dict]],
        data_type: str,
        collection_name: str,
        output_dir: Path = Path("generated_dataset"),
    ) -> None:
        output_dir.mkdir(exist_ok=True)

        try:
            logger.info(f"Starting to push data to Comet: {collection_name}")

            # Assuming the settings module has been properly configured with the required attributes
            experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE,
            )

            training_data, testing_data = train_test_split

            file_name_training_data = output_dir / f"{collection_name}_training.json"
            file_name_testing_data = output_dir / f"{collection_name}_testing.json"

            logging.info(f"Writing training data to file: {file_name_training_data}")
            with file_name_training_data.open("w") as f:
                json.dump(training_data, f)

            logging.info(f"Writing testing data to file: {file_name_testing_data}")
            with file_name_testing_data.open("w") as f:
                json.dump(testing_data, f)

            logger.info("Data written to file successfully")

            artifact = Artifact(f"{data_type}-instruct-dataset")
            artifact.add(file_name_training_data)
            artifact.add(file_name_testing_data)
            logger.info(f"Artifact created.")

            experiment.log_artifact(artifact)
            experiment.end()
            logger.info("Artifact pushed to Comet successfully.")

        except Exception:
            logger.exception(
                f"Failed to create Comet artifact and push it to Comet.",
            )

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
    file_handler = FileHandler()
    api_communicator = GptCommunicator()
    data_formatter = DataFormatter()
    dataset_generator = DatasetGenerator(file_handler, api_communicator, data_formatter)

    collections = [
        ("cleaned_articles", "articles"),
        ("cleaned_repositories", "repositories"),
    ]
    for collection_name, data_type in collections:
        logger.info(
            "Generating training data.",
            collection_name=collection_name,
            data_type=data_type,
        )

        dataset_generator.generate_training_data(
            collection_name=collection_name, data_type=data_type
        )
