import os
from typing import Tuple

import pandas as pd
import qwak
import torch as th
import yaml
from comet_ml import Experiment
from datasets import DatasetDict, load_dataset
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from qwak.model.adapters import DefaultOutputAdapter
from qwak.model.base import QwakModel
from qwak.model.schema import ModelSchema
from qwak.model.schema_entities import InferenceOutput, RequestInput
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    PreTrainedModel,
    Trainer,
    TrainingArguments,
)

from finetuning.dataset_client import DatasetClient
from finetuning.settings import settings
from finetuning.utils import build_qlora_model, get_logger

logger = get_logger(__name__)


class CopywriterMistralModel(QwakModel):
    def __init__(
        self,
        use_experiment_tracker: bool = True,
        register_model_to_model_registry: bool = True,
        model_type: str = "mistralai/Mistral-7B-Instruct-v0.3",
        fine_tuned_llm_twin_model_type: str = settings.FINE_TUNED_LLM_TWIN_MODEL_TYPE,
        dataset_artifact_name: str = settings.DATASET_ARTIFACT_NAME,
        config_file: str = settings.CONFIG_FILE,
        model_save_dir: str = settings.MODEL_SAVE_DIR,
    ) -> None:
        self._prep_environment()

        self.use_experiment_tracker = use_experiment_tracker
        self.register_model_to_model_registry = register_model_to_model_registry
        self.model_save_dir = model_save_dir
        self.model_type = model_type
        self.fine_tuned_llm_twin_model_type = fine_tuned_llm_twin_model_type
        self.dataset_artifact_name = dataset_artifact_name
        self.training_args_config_file = config_file
        self.device = th.device("cuda" if th.cuda.is_available() else "cpu")

    def _prep_environment(self) -> None:
        os.environ["TOKENIZERS_PARALLELISM"] = settings.TOKENIZERS_PARALLELISM
        th.cuda.empty_cache()
        logger.info("Emptied cuda cache. Environment prepared successfully!")

        assert settings.HUGGINGFACE_ACCESS_TOKEN, "HUGGINGFACE_ACCESS_TOKEN must be set"

    def build(self) -> None:
        self.nf4_config = self._init_4bit_config()
        self.model, self.tokenizer = self.init_model(self.nf4_config)
        tokenized_datasets = self.load_dataset()

        if self.use_experiment_tracker:
            assert settings.COMET_API_KEY, "COMET_API_KEY must be set"
            assert settings.COMET_PROJECT, "COMET_PROJECT must be set"
            assert settings.COMET_WORKSPACE, "COMET_WORKSPACE must be set"

            self.experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE,
            )
        else:
            self.experiment = None

        self.model, self.qlora_config = self._initialize_qlora(self.model)
        self.training_arguments = self._init_trainig_args()

        if self.experiment:
            self.experiment.log_parameters(self.nf4_config, prefix="bitsandbytes_")
            self.experiment.log_parameters(self.training_arguments, prefix="training_")
            self.experiment.log_parameters(self.qlora_config, prefix="qlora_")

        self.model = self.model.to(self.device)

        self.trainer = Trainer(
            model=self.model,
            args=self.training_arguments,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            tokenizer=self.tokenizer,
        )
        logger.info("Initialized model trainer")
        self.trainer.train()
        logger.info("Finished training LLM.", model_type=self.model_type)
        self.trainer.save_model(self.model_save_dir)
        logger.info("Finished saving model.", model_save_dir=self.model_save_dir)

        if self.experiment:
            self.experiment.log_model("llm-twin", self.model_save_dir)
            if self.register_model_to_model_registry:
                self.experiment.register_model(
                    "llm-twin",
                    workspace=settings.COMET_WORKSPACE,
                    registry_name="llm-twin",
                    public=True,
                    tags=["lora-weights", "qwak-training-pipeline"],
                )

            self.experiment.end()

        self._remove_model_class_attributes()

    def _init_4bit_config(self) -> BitsAndBytesConfig:
        nf4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=th.bfloat16,
        )

        logger.info(
            "Initialized config for param representation on 4bits successfully!"
        )

        return nf4_config

    def init_model(self, bnb_config: BitsAndBytesConfig) -> tuple:
        model = AutoModelForCausalLM.from_pretrained(
            self.model_type,
            token=settings.HUGGINGFACE_ACCESS_TOKEN,
            device_map="auto" if th.cuda.is_available() else "cpu",
            quantization_config=bnb_config,
            use_cache=False,
            torchscript=True,
            cache_dir=settings.CACHE_DIR,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_type,
            token=settings.HUGGINGFACE_ACCESS_TOKEN,
            cache_dir=settings.CACHE_DIR,
        )
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        logger.info("Initialized model successfully", model_type=self.model_type)

        return model, tokenizer

    def _initialize_qlora(self, model: PreTrainedModel) -> Tuple[PeftModel, LoraConfig]:
        qlora_config = LoraConfig(
            lora_alpha=16, lora_dropout=0.1, r=64, bias="none", task_type="CAUSAL_LM"
        )

        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, qlora_config)

        logger.info("Initialized QLoRA config successfully!")

        return model, qlora_config

    def _init_trainig_args(self) -> TrainingArguments:
        with open(self.training_args_config_file, "r") as file:
            config = yaml.safe_load(file)
        training_arguments = TrainingArguments(**config["training_arguments"])

        logger.info("Initialized training arguments successfully!")

        return training_arguments

    def load_dataset(self) -> DatasetDict:
        dataset_handler = DatasetClient()
        train_data_file, validation_data_file = dataset_handler.download_dataset(
            self.dataset_artifact_name
        )
        data_files = {
            "train": str(train_data_file),
            "validation": str(validation_data_file),
        }
        train_val_datasets = load_dataset("json", data_files=data_files)
        train_dataset, val_dataset = self.preprocess_data_split(train_val_datasets)

        return DatasetDict({"train": train_dataset, "validation": val_dataset})

    def preprocess_data_split(self, train_val_datasets: DatasetDict) -> tuple:
        train_data = train_val_datasets["train"]
        val_data = train_val_datasets["validation"]

        generated_train_dataset = train_data.map(self.generate_prompt)
        generated_train_dataset = generated_train_dataset.remove_columns(
            ["instruction", "content"]
        )
        generated_val_dataset = val_data.map(self.generate_prompt)
        generated_val_dataset = generated_val_dataset.remove_columns(
            ["instruction", "content"]
        )

        return generated_train_dataset, generated_val_dataset

    def _remove_model_class_attributes(self) -> None:
        # Remove class attributes to skip default
        # serialization with Pickle done by Qwak

        if getattr(self, "model", None):
            del self.model
        if getattr(self, "trainer", None):
            del self.trainer
        if getattr(self, "experiment", None):
            del self.experiment

    def generate_prompt(self, sample: dict) -> dict:
        full_prompt = f"""<s>[INST]{sample['instruction']}
        [/INST] {sample['content']}</s>"""
        result = self.tokenize(full_prompt)

        return result

    def tokenize(self, prompt: str) -> dict:
        result = self.tokenizer(
            prompt,
            padding="max_length",
            max_length=2300,
            truncation=True,
        )
        result["labels"] = result["input_ids"].copy()

        return result

    def initialize_model(self) -> None:
        self.model, self.tokenizer, _ = build_qlora_model(
            pretrained_model_name_or_path=self.model_type,
            peft_pretrained_model_name_or_path=self.fine_tuned_llm_twin_model_type,
            bnb_config=self.nf4_config,
            lora_config=self.qlora_config,
            cache_dir=settings.CACHE_DIR,
        )
        self.model = self.model.to(self.device)

        logger.info(
            "Successfully loaded model from.", model_save_dir=self.model_save_dir
        )

    def schema(self) -> ModelSchema:
        return ModelSchema(
            inputs=[RequestInput(name="instruction", type=str)],
            outputs=[InferenceOutput(name="content", type=str)],
        )

    @qwak.api(output_adapter=DefaultOutputAdapter())
    def predict(self, df) -> pd.DataFrame:
        input_text = list(df["instruction"].values)
        input_ids = self.tokenizer(
            input_text, return_tensors="pt", add_special_tokens=True
        )
        input_ids = input_ids.to(self.device)

        generated_ids = self.model.generate(
            **input_ids,
            max_new_tokens=500,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        answer_start_idx = input_ids["input_ids"].shape[1]
        generated_answer_ids = generated_ids[:, answer_start_idx:]
        decoded_output = self.tokenizer.batch_decode(generated_answer_ids)[0]

        return pd.DataFrame([{"content": decoded_output}])
