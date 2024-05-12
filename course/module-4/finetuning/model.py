import logging

import pandas as pd
import qwak
from datasets import load_dataset, DatasetDict
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from qwak.model.adapters import DefaultOutputAdapter
from qwak.model.base import QwakModel
import torch as th
from qwak.model.schema import ModelSchema
from qwak.model.schema_entities import RequestInput, InferenceOutput
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, BitsAndBytesConfig, \
    AutoModelForCausalLM
from comet_ml import Experiment
from comet_ml.integration.pytorch import log_model
import os

from settings import settings


class CopywriterModel(QwakModel):
    def __init__(self, is_saved: bool = False, train_data_file: str = "./linkedin-train.json",
                 validation_data_file: str = "./linkedin-validation.json", model_save_dir: str = "./model"):
        self._prep_environment()
        self.OPENAI_API_KEY = settings.OPENAI_API_KEY
        self.experiment = None
        self.data_files = {"train": train_data_file, "validation": validation_data_file}
        self.model_save_dir = model_save_dir
        self.model_type = "mistralai/Mistral-7B-Instruct-v0.1"
        if is_saved:
            self.experiment = Experiment(
                api_key=settings.COMET_API_KEY,
                project_name=settings.COMET_PROJECT,
                workspace=settings.COMET_WORKSPACE
            )

    def _prep_environment(self):
        os.environ["TOKENIZERS_PARALLELISM"] = settings.TOKENIZERS_PARALLELISM
        th.cuda.empty_cache()
        logging.info("Emptied cuda cache. Environment prepared successfully!")

    def init_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_type,
            token=self.OPENAI_API_KEY,
            device_map=th.cuda.current_device(),
            quantization_config=self.nf4_config,
            use_cache=False,
            torchscript=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_type, token=self.OPENAI_API_KEY)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        logging.info("Initialized model successfully!")

    def _init_4bit_config(self):
        self.nf4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=th.bfloat16
        )
        if self.experiment:
            self.experiment.log_parameters(self.nf4_config)
        logging.info("Initialized config for param representation on 4bits successfully!")

    def _init_qlora_config(self):
        self.qlora_config = LoraConfig(
            lora_alpha=16,
            lora_dropout=0.1,
            r=64,
            bias="none",
            task_type="CAUSAL_LM"
        )

        if self.experiment:
            self.experiment.log_parameters(self.qlora_config)

        self.model = prepare_model_for_kbit_training(self.model)
        self.model = get_peft_model(self.model, self.qlora_config)
        if self.experiment:
            log_model(self.experiment, model=self.model, model_name="Copywriter-v1")
        logging.info("Initialized qlora config successfully!")

    def _init_trainig_args(self):
        self.training_arguments = TrainingArguments(
            output_dir="mistral_instruct_generation",
            max_steps=10,
            per_device_train_batch_size=1,
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="steps",
            eval_steps=2,
            learning_rate=2e-4,
            fp16=True,
            remove_unused_columns=False,
            lr_scheduler_type='constant',
        )
        if self.experiment:
            self.experiment.log_parameters(self.training_arguments)
        logging.info("Initialized training arguments successfully!")

    def _remove_class_attributes(self):
        del self.model
        del self.trained_model

    def generate_prompt(self, sample):
        full_prompt = f"""<s>[INST]{sample['instruction']}
        [/INST] {sample['content']}</s>"""
        result = self.tokenize(full_prompt)
        return result

    def tokenize(self, prompt):
        result = self.tokenizer(
            prompt,
            padding="max_length",
            max_length=2300,
            truncation=True,
        )
        result["labels"] = result["input_ids"].copy()
        return result

    def load_dataset(self):
        raw_datasets = load_dataset("json", data_files=self.data_files)
        train_data = raw_datasets['train']
        val_data = raw_datasets['validation']
        generated_train_dataset = train_data.map(self.generate_prompt)
        generated_train_dataset = generated_train_dataset.remove_columns(["instruction", "content"])
        generated_val_dataset = val_data.map(self.generate_prompt)
        generated_val_dataset = generated_val_dataset.remove_columns(["instruction", "content"])
        return DatasetDict({
            'train': generated_train_dataset,
            'validation': generated_val_dataset
        })

    def build(self):
        self._init_4bit_config()
        self.init_model()
        self.model = prepare_model_for_kbit_training(self.model)
        if self.experiment:
            self.experiment.log_parameters(self.nf4_config)
        self._init_qlora_config()
        self._init_trainig_args()
        tokenized_datasets = self.load_dataset()
        self.device = th.device("cuda" if th.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.trained_model = Trainer(
            model=self.model,
            args=self.training_arguments,
            train_dataset=tokenized_datasets['train'],
            eval_dataset=tokenized_datasets['validation'],
            tokenizer=self.tokenizer,
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
        )
        logging.info("Initialized model trainer")
        self.trained_model.train()
        logging.info("Finished model finetuning!")
        self.trained_model.save_model(self.model_save_dir)
        logging.info(f'Finished saving model to {self.model_save_dir}')
        self._remove_class_attributes()
        logging.info("Finished removing model class attributes!")

    def initialize_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_save_dir, token=self.OPENAI_API_KEY,
                                                          quantization_config=self.nf4_config)
        logging.info(f'Successfully loaded model from {self.model_save_dir}')

    def schema(self) -> ModelSchema:
        return ModelSchema(inputs=[RequestInput(name="instruction", type=str)],
                           outputs=[InferenceOutput(name="content", type=str)])

    @qwak.api(output_adapter=DefaultOutputAdapter())
    def predict(self, df):
        input_text = list(df['instruction'].values)
        input_ids = self.tokenizer(input_text, return_tensors="pt", add_special_tokens=True)
        input_ids = input_ids.to(self.device)

        generated_ids = self.model.generate(**input_ids, max_new_tokens=3000, do_sample=True,
                                            pad_token_id=self.tokenizer.eos_token_id)

        decoded_output = self.tokenizer.batch_decode(generated_ids)

        return pd.DataFrame([{"content": decoded_output}])
