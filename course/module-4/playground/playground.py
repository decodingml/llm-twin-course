import comet_ml

experiment = comet_ml.Experiment(
    api_key="IONOUb5MOWypnlCl1iB6rVDxx",
    project_name="llm-twin-mistral7b-inst",
    workspace="joywalker",
)

artifact = comet_ml.Artifact(name="cleaned_posts", artifact_type="dataset")

files = [
    "linkedin-train.json",
    "linkedin-validation.json",
]
for file_path in files:
    artifact.add(file_path)

experiment.log_artifact(artifact)
experiment.end()
