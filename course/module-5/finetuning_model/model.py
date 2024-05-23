import logging
import os

import comet_ml
import pandas as pd
import qwak
import torch as th
import yaml
from comet_ml import Experiment
from datasets import DatasetDict, load_dataset
from finetuning_model.dataset_client import DatasetClient
from finetuning_model.settings import settings
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


class CopywriterMistralModel(QwakModel):
    def __init__(
        self,
        is_saved: bool = False,
        model_save_dir: str = "./model",
        model_type: str = "mistralai/Mistral-7B-Instruct-v0.1",
        comet_artifact_name: str = "cleaned_posts",
        config_file: str = "./finetuning_model/config.yaml",
    ):
        self._prep_environment()
        self.experiment = None
        self.model_save_dir = model_save_dir
        self.model_type = model_type
        self.comet_dataset_artifact = comet_artifact_name
        self.training_args_config_file = config_file
        if is_saved:
            self.experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE,
            )

    def _prep_environment(self):
        os.environ["TOKENIZERS_PARALLELISM"] = settings.TOKENIZERS_PARALLELISM
        th.cuda.empty_cache()
        logging.info("Emptied cuda cache. Environment prepared successfully!")

    def init_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_type,
            token=settings.HUGGINGFACE_ACCESS_TOKEN,
            device_map=th.cuda.current_device(),
            quantization_config=self.nf4_config,
            use_cache=False,
            torchscript=True,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_type, token=settings.HUGGINGFACE_ACCESS_TOKEN
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        logging.info(f"Initialized model{self.model_type} successfully")

    def _init_4bit_config(self):
        self.nf4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=th.bfloat16,
        )
        if self.experiment:
            self.experiment.log_parameters(self.nf4_config)
        logging.info(
            "Initialized config for param representation on 4bits successfully!"
        )

    def _initialize_qlora(self, model: PreTrainedModel) -> PeftModel:
        self.qlora_config = LoraConfig(
            lora_alpha=16, lora_dropout=0.1, r=64, bias="none", task_type="CAUSAL_LM"
        )

        if self.experiment:
            self.experiment.log_parameters(self.qlora_config)

        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, self.qlora_config)
        logging.info("Initialized qlora config successfully!")
        return model

    def _init_trainig_args(self):
        with open(self.training_args_config_file, "r") as file:
            config = yaml.safe_load(file)
        self.training_arguments = TrainingArguments(**config["training_arguments"])
        if self.experiment:
            self.experiment.log_parameters(self.training_arguments)
        logging.info("Initialized training arguments successfully!")

    def _remove_model_class_attributes(self):
        # remove needed in order to skip default serialization with Pickle done by Qwak
        del self.model
        del self.trainer
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
            max_length=100,
            truncation=True,
        )
        result["labels"] = result["input_ids"].copy()
        return result

    def load_dataset(self) -> DatasetDict:
        dataset_handler = DatasetClient()
        train_data_file, validation_data_file = dataset_handler.download_dataset(
            self.comet_dataset_artifact
        )
        data_files = {"train": train_data_file, "validation": validation_data_file}
        raw_datasets = load_dataset("json", data_files=data_files)
        train_dataset, val_dataset = self.preprocess_data_split(raw_datasets)
        return DatasetDict({"train": train_dataset, "validation": val_dataset})

    def preprocess_data_split(self, raw_datasets: DatasetDict):
        train_data = raw_datasets["train"]
        val_data = raw_datasets["validation"]
        generated_train_dataset = train_data.map(self.generate_prompt)
        generated_train_dataset = generated_train_dataset.remove_columns(
            ["instruction", "content"]
        )
        generated_val_dataset = val_data.map(self.generate_prompt)
        generated_val_dataset = generated_val_dataset.remove_columns(
            ["instruction", "content"]
        )
        return generated_train_dataset, generated_val_dataset

    def build(self):
        self._init_4bit_config()
        self.init_model()
        if self.experiment:
            self.experiment.log_parameters(self.nf4_config)
        self.model = self._initialize_qlora(self.model)
        self._init_trainig_args()
        tokenized_datasets = self.load_dataset()
        self.device = th.device("cuda" if th.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.trainer = Trainer(
            model=self.model,
            args=self.training_arguments,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            tokenizer=self.tokenizer,
        )
        logging.info("Initialized model trainer")
        self.trainer.train()
        logging.info("Finished model finetuning_model!")
        self.trainer.save_model(self.model_save_dir)
        logging.info(f"Finished saving model to {self.model_save_dir}")
        self.experiment.end()
        self._remove_model_class_attributes()
        logging.info("Finished removing model class attributes!")

    def initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_save_dir,
            token=settings.HUGGINGFACE_ACCESS_TOKEN,
            quantization_config=self.nf4_config,
        )
        logging.info(f"Successfully loaded model from {self.model_save_dir}")

    def schema(self) -> ModelSchema:
        return ModelSchema(
            inputs=[RequestInput(name="instruction", type=str)],
            outputs=[InferenceOutput(name="content", type=str)],
        )

    @qwak.api(output_adapter=DefaultOutputAdapter())
    def predict(self, df):
        input_text = list(df["instruction"].values)
        input_ids = self.tokenizer(
            input_text, return_tensors="pt", add_special_tokens=True
        )
        input_ids = input_ids.to(self.device)

        generated_ids = self.model.generate(
            **input_ids,
            max_new_tokens=3000,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        decoded_output = self.tokenizer.batch_decode(generated_ids)

        return pd.DataFrame([{"content": decoded_output}])
