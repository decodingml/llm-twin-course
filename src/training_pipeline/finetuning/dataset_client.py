import json
from pathlib import Path

from comet_ml import Artifact, Experiment
from comet_ml.artifacts import ArtifactAsset
from sklearn.model_selection import train_test_split

from finetuning.settings import settings
from finetuning.utils import get_logger

logger = get_logger(__file__)


class DatasetClient:
    def __init__(self, output_dir: Path = Path("./finetuning_dataset")):
        self.project = settings.COMET_PROJECT
        self.api_key = settings.COMET_API_KEY

        self.experiment = Experiment(api_key=self.api_key, project_name=self.project)

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_dataset(self, artifact_name: str) -> tuple:
        artifact = self._download_artifact(artifact_name)
        asset = self._artifact_to_asset(artifact)
        data = self._load_data(asset)
        train_val_paths = self._split_data(data)

        return train_val_paths

    def _download_artifact(self, artifact_name: str) -> Artifact:
        try:
            logged_artifact = self.experiment.get_artifact(artifact_name)
            artifact = logged_artifact.download(self.output_dir)
        except Exception as e:
            logger.error(f"Error retrieving artifact: {str(e)}")

            raise

        self.experiment.end()

        logger.info(
            f"Successfully downloaded  {artifact_name} at location {self.output_dir}"
        )

        return artifact

    def _artifact_to_asset(self, artifact: Artifact) -> str:
        if len(artifact.assets) == 0:
            raise RuntimeError("Artifact has no assets")
        elif len(artifact.assets) > 1:
            raise RuntimeError("Artifact has more than one asset")
        else:
            asset = artifact.assets[0]

        return asset

    def _load_data(self, asset: ArtifactAsset) -> list:
        data_file_path = asset.local_path_or_data
        with open(data_file_path, "r") as file:
            data = json.load(file)

        return [{k: str(v) for k, v in data_point.items()} for data_point in data]

    def _split_data(self, data: list) -> tuple:
        train_data, validation_data = train_test_split(
            data, test_size=0.1, random_state=42
        )

        training_data_path = self.output_dir / "train.json"
        validation_data_path = self.output_dir / "validation.json"

        for data_path, data_split in (
            (training_data_path, train_data),
            (validation_data_path, validation_data),
        ):
            with open(data_path, "w") as file:
                json.dump(data_split, file)

        return training_data_path, validation_data_path
