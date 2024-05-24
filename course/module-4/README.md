# Introduction

---

This module reflects the LLM fine-tuning pipeline where we download versioned datsets from CometML and manage the deployment at scale using Qwak.
**Completing this lesson**, you'll gain a solid understanding of the following:

- what is Qwak AI and how does it help solve MLOps challenges
- how to fine-tune a Mistral7b-Instruct on our custom llm-twin dataset
- what is PEFT (parameter-efficient-fine-tuning)
- what purpose do QLoRA Adapters and BitsAndBytes configs serve
- how to fetch versioned datasets from CometML
- how to log training metrics and model to CometML
- understanding model-specific special tokens
- the detailed walkthrough of how the Qwak build system works

# What is fine-tuning ?

---

Represents the process of taking pre-trained models and further training them on smaller, specific datasets to refine their capabilities and improve performance in a particular task or domain. Fine-tuning is about turning general-purpose models and turning them into specialized models.

> [!IMPORTANT]
> Foundation models know a lot about a lot, but for production, we need models that know a lot about a little.

In our LLM-Twin use case, we're aiming to fine-tune our model from a general knowledge corpora towards a targeted context that reflects your writing persona.

We're using the following concepts widely adopted when Fine-Tuning LLMs:

- [PEFT](https://huggingface.co/docs/peft/en/index) - Parameter Efficient Fine Tuning
- [QLoRA](https://github.com/microsoft/LoRA) - Quantized Low Rank Adaptation
- [BitsAndBytes](https://huggingface.co/blog/4bit-transformers-bitsandbytes) - Library to allow low-precision operations over custom GPU kernels

You can learn more about the Dataset Generation and Fine-tuning Pipeline from Decoding ML LLM Twin Course:

- Lesson 6: [The Role of Feature Stores in Fine-Tuning LLMs](https://medium.com/decodingml/the-role-of-feature-stores-in-fine-tuning-llms-22bd60afd4b9)
- Lesson 7: TBD

## Refresher from Previous Lessons

- In **Lesson 2** : [The Importance of Data Pipelines in the Era of Generative AI](https://medium.com/decodingml/the-importance-of-data-pipelines-in-the-era-of-generative-ai-673e1505a861)
  We've described the process of data ingestion where we're scrapping articles from Medium, posts from LinkedIn, and Code snippets from GitHub and storing them in our Mongo Database.
- In **Lesson 3** : [Change Data Capture: Enabling Event-Driven Architectures](https://medium.com/decodingml/the-3nd-out-of-11-lessons-of-the-llm-twin-free-course-ba82752dad5a)
  We've showcased how to listen to MongoDB Oplog via the CDC pattern, and adapt RabbitMQ to stream captured events, this is our ingestion pipeline.
- In **Lesson 6**: [The Role of Feature Stores in Fine-Tuning LLMs](https://medium.com/decodingml/the-role-of-feature-stores-in-fine-tuning-llms-22bd60afd4b9)
  We've showcased how to use filtered data samples from QDrant. Using Knowledge Distillation, we have the GPT3.5 Turbo to structure and generate the fine-tuning dataset that is versioned with CometML.

---

# Architecture Overview

![Architecture](./media/fine-tuning-workflow.png)

**Here's what we're going to learn**:

- Set-up the HuggingFace connection to be able to download Mistral7b-Instruct model.
- Learn how to leverage Qwak to manage our training job at scale.
- How to efficiently fine-tune a large model using PEFT & QLoRA
- How to download datasets versioned with CometML
- How does the Qwak Build Lifecycle works

# Dependencies

## Installation and Setup

To prepare your environment for these components, follow these steps:

- `poetry init`
- `poetry install`

# HuggingFace Integration

---

To be able to download the model checkpoint, and further use it for fine-tuning, we need a Hugging Face Access Token.
**Here's how to get it:**

- Log-in to [HuggingFace](https://huggingface.co)
- Head over to your profile (top-left) and click on Settings.
- On the left panel, go to Access Tokens and generate a new Token
- Save the Token

# CometML Integration

---

## Overview

[CometML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) is a cloud-based platform that provides tools for tracking, comparing, explaining, and optimizing experiments and models in machine learning. CometML helps data scientists and teams to better manage and collaborate on machine learning experiments.

## Why Use CometML?

- **Experiment Tracking**: CometML automatically tracks your code, experiments, and results, allowing you to compare between different runs and configurations visually.
- **Model Optimization**: It offers tools to compare different models side by side, analyze hyperparameters, and track model performance across various metrics.
- **Collaboration and Sharing**: Share findings and models with colleagues or the ML community, enhancing team collaboration and knowledge transfer.
- **Reproducibility**: By logging every detail of the experiment setup, CometML ensures experiments are reproducible, making it easier to debug and iterate.

## CometML Variables

When integrating CometML into your projects, you'll need to set up several environment variables to manage the authentication and configuration:

- `COMET_API_KEY`: Your unique API key that authenticates your interactions with the CometML API.
- `COMET_PROJECT`: The project name under which your experiments will be logged.
- `COMET_WORKSPACE`: The workspace name that organizes various projects and experiments.

## Obtaining CometML Variables

To access and set up the necessary CometML variables for your project, follow these steps:

1. **Create an Account or Log In**:

   - Visit [CometML's website](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) and log in if you already have an account, or sign up if you're a new user.

2. **Create a New Project**:

   - Once logged in, navigate to your dashboard. Here, you can create a new project by clicking on "New Project" and entering the relevant details for your project.

3. **Access API Key**:

   - After creating your project, you will need to obtain your API key. Navigate to your account settings by clicking on your profile at the top right corner. Select 'API Keys' from the menu, and you'll see an option to generate or copy your existing API key.

4. **Set Environment Variables**:
   - These variables, `COMET_API_KEY`, `COMET_PROJECT` and `COMET_WORKSPACE`, should be added in the `build_config.yaml` when deploying on qwak. Follow the next module to integrate Qwak.

# Qwak Integration

---

## Overview

[Qwak](https://www.qwak.com/lp/end-to-end-mlops/?utm_source=medium&utm_medium=referral&utm_campaign=decodingml) is an all-in-one MLOps platform designed to streamline the entire machine learning lifecycle from data preparation to deployment and monitoring. It offers a comprehensive suite of tools that allow data science teams to build, train, deploy, manage, and monitor AI and machine learning models efficiently.

## Why Use Qwak?

Qwak is used by a range of companies across various industries, from banking and finance to e-commerce and technology, underscoring its versatility and effectiveness in handling diverse AI and ML needs. Here are a few reasons:

- **End-to-End MLOps Platform**: Qwak provides tools for every stage of the machine learning lifecycle, including data preparation, model training, deployment, and monitoring. This integration helps eliminate the need for multiple disparate tools and simplifies the workflow for data science teams
- **Integration with Existing Tools**: Qwak supports integrations with popular tools and platforms such as HuggingFace, Snowflake, Kafka, PostgreSQL, and more, facilitating seamless incorporation into existing workflows and infrastructure​.
- **User-Friendly Interface**: Qwak offers a user-friendly interface and managed Jupyter notebooks, making it accessible for both experienced data scientists and those new to the field​
- **Smooth Developer Experience**: The CLI sdk is very intuitive and easy to use, and allows developers to scale inference/training jobs accordingly without the hassle of managing infrastructure.

## Setting Up Qwak

[Qwak.ai](https://www.qwak.com/lp/end-to-end-mlops/?utm_source=medium&utm_medium=referral&utm_campaign=decodingml) is straightforward and easy to set-up.

To configure your environment for Qwak, log in to [Qwak.ai](https://www.qwak.com/lp/end-to-end-mlops/?utm_source=medium&utm_medium=referral&utm_campaign=decodingml) and go to your profile → settings → Account Settings → Personal API Keys and generate a new key.

In your terminal, run `qwak configure` and it'll ask you for your `API-KEY`, paste it and you're done!

## Creating a new Qwak Model

In order to deploy model versions remotely on qwak, first you'll have to initialize a `model` and a `project`. To do that, run in the terminal:

```
qwak models create "ModelName" --project "ProjectName"
```

Once you've done that, make sure you have these environment variables:

```plaintext
HUGGINGFACE_TOKEN="your-hugging-face-token"
COMET_API_KEY="your-key"
COMET_WORKSPACE="your-workspace"
COMET_PROJECT='your-project'
```

Now, populate the `env` variables in the `build_config.yaml` to complete the qwak deployment prerequisites.:

```
build_env:
  docker:
    assumed_iam_role_arn: null
    base_image: public.ecr.aws/qwak-us-east-1/qwak-base:0.0.13-gpu
    cache: true
    env_vars:
    - HUGGINGFACE_ACCESS_TOKEN=""
    - COMET_API_KEY=""
    - COMET_WORKSPACE=""
    - COMET_PROJECT=""
    no_cache: false
    params: []
    push: true
  python_env:
    dependency_file_path: finetuning/requirements.txt
    git_credentials: null
    git_credentials_secret: null
    poetry: null
    virtualenv: null
  remote:
    is_remote: true
    resources:
      cpus: null
      gpu_amount: null
      gpu_type: null
      instance: gpu.a10.2xl
      memory: null
build_properties:
  branch: finetuning
  build_id: null
  gpu_compatible: false
  model_id: ---MODEL_NAME---
  model_uri:
    dependency_required_folders: []
    git_branch: master
    git_credentials: null
    git_credentials_secret: null
    git_secret_ssh: null
    main_dir: finetuning
    uri: .
  tags: []
deploy: false
deployment_instance: null
post_build: null
pre_build: null
purchase_option: null
step:
  tests: true
  validate_build_artifact: true
  validate_build_artifact_timeout: 120
verbose: 0
```

# Usage

---

The project includes a `Makefile` for easy management of common tasks. Here are the main commands you can use:

- `make help`: Displays help for each make command.
- `make test`: Runs tests on local-qwak deployment.
- `make deploy`: Triggers a new fine-tuning job to Qwak remotely, using the configuration specified in `build_config.yaml`

# Meet your teachers!

---

The course is created under the [Decoding ML](https://decodingml.substack.com/) umbrella by:

<table>
  <tr>
    <td><a href="https://github.com/iusztinpaul" target="_blank"><img src="https://github.com/iusztinpaul.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Paul Iusztin</strong><br />
      <i>Senior ML & MLOps Engineer</i>
    </td>
  </tr>
  <tr>
    <td><a href="https://github.com/alexandruvesa" target="_blank"><img src="https://github.com/alexandruvesa.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Alexandru Vesa</strong><br />
      <i>Senior AI Engineer</i>
    </td>
  </tr>
  <tr>
    <td><a href="https://github.com/Joywalker" target="_blank"><img src="https://github.com/Joywalker.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Răzvanț Alexandru</strong><br />
      <i>Senior ML Engineer</i>
    </td>
  </tr>
</table>

# License

This course is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., university projects, college degree projects, personal projects, etc.).

# 🏆 Contribution

A big "Thank you 🙏" to all our contributors! This course is possible only because of their efforts.

<p align="center">
    <a href="https://github.com/decodingml/llm-twin-course/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=decodingml/llm-twin-course" />
    </a>
</p>
