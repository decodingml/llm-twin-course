import json
import os
import logging
from comet_ml import Experiment
from sklearn.model_selection import train_test_split

from finetuning.settings import settings
class DatasetClient:
    def __init__(self, output_dir: str = "./finetuning_model"):
        self.project = settings.COMET_PROJECT
        self.api_key = settings.COMET_API_KEY
        self.experiment = Experiment(
            api_key=self.api_key,
            project_name=self.project
        )
        self.output_dir = output_dir

    def get_artifact(self, artifact_name: str):
        try:
            logged_artifact = self.experiment.get_artifact(artifact_name)
            logged_artifact.download(self.output_dir)
            self.experiment.end()
            logging.info(f'Successfully downloaded  {artifact_name} at location {self.output_dir}')
        except Exception as e:
            logging.error(f"Error retrieving artifact: {str(e)}")

    def split_data(self, artifact_name: str) -> tuple:
        try:
            training_file_path = os.path.join(self.output_dir, 'train.json')
            validation_file_path = os.path.join(self.output_dir, 'validation.json')
            file_name = artifact_name + ".json"
            with open(os.path.join(self.output_dir,file_name), 'r') as file:
                data = json.load(file)

            train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)

            with open(training_file_path, 'w') as train_file:
                json.dump(train_data, train_file)

            with open(validation_file_path, 'w') as val_file:
                json.dump(val_data, val_file)

            logging.info("Data split into train.json and validation.json successfully.")
            return training_file_path, validation_file_path
        except Exception as e:
            logging.error(f"Error splitting data: {str(e)}")

    def download_dataset(self, file_name: str):
        self.get_artifact(file_name)
        return self.split_data(file_name)


