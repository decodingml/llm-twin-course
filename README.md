<div align="center">
    <h2>LLM Twin Course: Building Your Production-Ready AI Replica</h2>
    <h1>Learn to architect and implement a production-ready LLM & RAG system by building your LLM Twin</h1>
    <h3>From data gathering to productionizing LLMs using LLMOps good practices.</h3>
    <i>by <a href="https://decodingml.substack.com">Decoding ML</i>
</div>

</br>

<p align="center">
  <img src="media/cover.png" alt="Your image description">
</p>

## Why is this course different?

*By finishing the **"LLM Twin: Building Your Production-Ready AI Replica"** free course, you will learn how to design, train, and deploy a production-ready LLM twin of yourself powered by LLMs, vector DBs, and LLMOps good practices.*

> Why should you care? 🫵
> 
> → **No more isolated scripts or Notebooks!** Learn production ML by building and deploying an end-to-end production-grade LLM system.


## What will you learn to build by the end of this course?

You will **learn** how to **architect** and **build a real-world LLM system** from **start** to **finish** - from **data collection** to **deployment**.

You will also **learn** to **leverage MLOps best practices**, such as experiment trackers, model registries, prompt monitoring, and versioning.

**The end goal?** Build and deploy your own LLM twin.

**What is an LLM Twin?** It is an AI character that learns to write like somebody by incorporating its style and personality into an LLM.

## Table of contents

- [1. The architecture of the LLM Twin is split into 4 Python microservices:](#the-architecture-of-the-llm-twin-is-split-into-4-python-microservices)
    - [1.1. The data collection pipeline](#the-data-collection-pipeline)
    - [1.2. The feature pipeline](#the-feature-pipeline)
    - [1.3. The training pipeline](#the-training-pipeline)
    - [1.4. The inference pipeline](#the-inference-pipeline)
- [2. Who is this for?](#who-is-this-for)
- [3. How will you learn?](#how-will-you-learn)
- [4. Costs?](#costs)
- [5. Questions and troubleshooting](#questions-and-troubleshooting)
- [6. Lessons](#lessons)
    - [6.1. System design](#system-design)
    - [6.2. Data engineering: Gather & store the data for your LLM twin](#data-engineering-gather--store-the-data-for-your-llm-twin)
    - [6.3. Feature pipeline: prepare data for LLM fine-tuning & RAG](#feature-pipeline-prepare-data-for-llm-fine-tuning--rag)
    - [6.4. Training pipeline: fine-tune your LLM twin](#training-pipeline-fine-tune-your-llm-twin)
    - [6.5. Inference pipeline: serve your LLM twin](#inference-pipeline-serve-your-llm-twin)
    - [6.6. Bonus: refactor and optimize the RAG system](#bonus-refactor-and-optimize-the-rag-system)
- [7. Install & Usage](#install--usage)
- [8. License](#license)
- [9. Contributors](#contributors)
- [10. Sponsors](#sponsors)
- [11. Next steps 🧑‍💻](#next-steps)

## The architecture of the LLM Twin is split into 4 Python microservices:

<p align="center">
  <img src="media/architecture.png" alt="LLM Twin Architecture">
</p>

### The data collection pipeline

- Crawl your digital data from various social media platforms, such as Medium, Substack and GitHub.
- Clean, normalize and load the data to a [Mongo NoSQL DB](https://www.mongodb.com/) through a series of ETL pipelines.
- Send database changes to a [RabbitMQ](https://www.rabbitmq.com/) queue using the CDC pattern.
- Learn to package the crawlers as AWS Lambda functions.

### The feature pipeline

- Consume messages in real-time from a queue through a [Bytewax](https://github.com/bytewax/bytewax?utm_source=github&utm_medium=decodingml&utm_campaign=2024_q1) streaming pipeline.
- Every message will be cleaned, chunked, embedded and loaded into a [Qdrant](https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course) vector DB.
- In the bonus series, we refactor the cleaning, chunking, and embedding logic using [Superlinked](https://github.com/superlinked/superlinked?utm_source=community&utm_medium=github&utm_campaign=oscourse), a specialized vector compute engine. We will also load and index the vectors to a [Redis vector DB](https://redis.io/solutions/vector-search/).

### The training pipeline

- Create a custom instruction dataset based on your custom digital data to do SFT.
- Fine-tune an LLM using LoRA or QLoRA.
- Use [Comet ML's](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) experiment tracker to monitor the experiments.
- Evaluate the LLM using [Opik](https://github.com/comet-ml/opik)
- Save and version the best model to the [Hugging Face model registry](https://huggingface.co/models).
- Run and automate the training pipeline using [AWS SageMaker](https://aws.amazon.com/sagemaker/).

### The inference pipeline

- Load the fine-tuned LLM from the [Hugging Face model registry](https://huggingface.co/models).
- Deploy the LLM as a scalable REST API using [AWS SageMaker inference endpoints](https://aws.amazon.com/sagemaker/deploy/).
- Enhance the prompts using advanced RAG techniques.
- Monitor the prompts and LLM generated results using [Opik](https://github.com/comet-ml/opik)
- In the bonus series, we refactor the advanced RAG layer to write more optimal queries using [Superlinked](https://github.com/superlinked/superlinked?utm_source=community&utm_medium=github&utm_campaign=oscourse).
- Wrap up everything with a Gradio UI (as seen below) where you can start playing around with the LLM Twin to generate content that follows your writing style.

<p align="center">
  <img src="media/ui-example.png" alt="Gradio UI">
</p>

Along the 4 microservices, you will learn to integrate 4 serverless tools:

* [Comet ML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github) as your experiment tracker and data registry;
* [Qdrant](https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course) as your vector DB;
* [AWS SageMaker](https://aws.amazon.com/sagemaker/) as your ML infrastructure;
* [Opik](https://github.com/comet-ml/opik) as your prompt evaluation and monitoring tool.

## Who is this for?

**Audience:** MLE, DE, DS, or SWE who want to learn to engineer production-ready LLM & RAG systems using LLMOps good principles.

**Level:** intermediate

**Prerequisites:** basic knowledge of Python and ML

## How will you learn?

The course contains **10 hands-on written lessons** and the **open-source code** you can access on GitHub, showing how to build an end-to-end LLM system.

Also, it includes **2 bonus lessons** on how to **improve the RAG system**.

You can read everything at your own pace.


## Costs?
The **articles** and **code** are **completely free**. They will always remain free.

If you plan to run the code while reading it, you must know that we use several cloud tools that might generate additional costs.

**Pay as you go** 
- [AWS](https://aws.amazon.com/) offers accessible plans to new joiners.
    - For a new first-time account, you could get up to 300$ in free credits which are valid for 6 months. For more, consult the [AWS Offerings](https://aws.amazon.com/free/offers/) page.

**Freemium** (Free-of-Charge)
- [Qdrant](https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course)
- [Comet ML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github)
- [Opik](https://github.com/comet-ml/opik)

## Questions and troubleshooting

Please ask us any questions if anything gets confusing while studying the articles or running the code.

You can `ask any question` by `opening an issue` in this GitHub repository by clicking [here](https://github.com/decodingml/llm-twin-course/issues).

## Lessons

> [!IMPORTANT]
> **To understand the entire code step-by-step, check out our articles ↓**
> 
> `The course is split into 12 lessons. Every Medium article represents an independent lesson.`
>
> The lessons are NOT 1:1 with the folder structure!

### System design
1. [An End-to-End Framework for Production-Ready LLM Systems by Building Your LLM Twin](https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f)

### Data engineering: Gathering and storing the data for your LLM Twin
2. [Your Content is Gold: I Turned 3 Years of Blog Posts into an LLM Training](https://medium.com/decodingml/your-content-is-gold-i-turned-3-years-of-blog-posts-into-an-llm-training-d19c265bdd6e)
3. [I Replaced 1000 Lines of Polling Code with 50 Lines of CDC Magic](https://medium.com/decodingml/i-replaced-1000-lines-of-polling-code-with-50-lines-of-cdc-magic-4d31abd3bc3b)

### Feature pipeline: Feature engineering data for LLM fine-tuning & RAG
4. [SOTA Python Streaming Pipelines for Fine-tuning LLMs and RAG — in Real-Time!](https://medium.com/decodingml/sota-python-streaming-pipelines-for-fine-tuning-llms-and-rag-in-real-time-82eb07795b87)
5. [The 4 Advanced RAG Algorithms You Must Know to Implement](https://medium.com/decodingml/the-4-advanced-rag-algorithms-you-must-know-to-implement-5d0c7f1199d2)

### Training pipeline: Fine-tuning your LLM Twin
6. [Turning Raw Data Into Fine-Tuning Datasets](https://medium.com/decodingml/turning-raw-data-into-fine-tuning-datasets-dc83657d1280)
7. [8B Parameters, 1 GPU, No Problems: The Ultimate LLM Fine-tuning Pipeline](https://medium.com/decodingml/8b-parameters-1-gpu-no-problems-the-ultimate-llm-fine-tuning-pipeline-f68ef6c359c2)
8. [The Engineer’s Framework for LLM & RAG Evaluation](https://medium.com/decodingml/the-engineers-framework-for-llm-rag-evaluation-59897381c326)

### Inference pipeline: Serving and monitoring your LLM Twin
9. [Beyond Proof of Concept: Building RAG Systems That Scale](https://medium.com/decodingml/beyond-proof-of-concept-building-rag-systems-that-scale-e537d0eb063a)
10. [Prompt monitoring WIP]()

### Bonus: Refactoring and optimizing the RAG system
11. [Build a scalable RAG ingestion pipeline using 74.3% less code](https://medium.com/decodingml/build-a-scalable-rag-ingestion-pipeline-using-74-3-less-code-ac50095100d6)
12. [Build Multi-Index Advanced RAG Apps](https://medium.com/decodingml/build-multi-index-advanced-rag-apps-bd33d2f0ec5c)

## Install & Usage

To understand how to **install and run the LLM Twin code end-to-end**, go to the [INSTALL_AND_USAGE](https://github.com/decodingml/llm-twin-course/blob/main/INSTALL_AND_USAGE.md) dedicated document.

> [!NOTE]
> Even though you can run everything solely using the [INSTALL_AND_USAGE](https://github.com/decodingml/llm-twin-course/blob/main/INSTALL_AND_USAGE.md) dedicated document, we recommend that you read the articles to understand the LLM Twin system and design choices fully.

### Bonus Superlinked series

The **bonus Superlinked series** has an extra dedicated [README](https://github.com/decodingml/llm-twin-course/blob/main/6-bonus-superlinked-rag/README.md) that you can access under the [src/bonus_superlinked_rag](https://github.com/decodingml/llm-twin-course/tree/main/src/bonus_superlinked_rag) directory.

In that section, we explain how to run it with the improved RAG layer powered by [Superlinked](https://github.com/superlinked/superlinked?utm_source=community&utm_medium=github&utm_campaign=oscourse).

## License

This course is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., university projects, college degree projects, personal projects, etc.).

## Contributors

A big "Thank you 🙏" to all our contributors! This course is possible only because of their efforts.

<p align="center">
    <a href="https://github.com/decodingml/llm-twin-course/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=decodingml/llm-twin-course" />
    </a>
</p>

## Sponsors

Also, another big "Thank you 🙏" to all our sponsors who supported our work and made this course possible. 

<table>
  <tr>
    <td align="center">
      <a href="https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github" target="_blank">Comet</a>
    </td>
    <td align="center">
      <a href="https://github.com/comet-ml/opik" target="_blank">Opik</a>
    </td>
    <td align="center">
      <a href="https://github.com/bytewax/bytewax?utm_source=github&utm_medium=decodingml&utm_campaign=2024_q1" target="_blank">Bytewax</a>
    </td>
    <td align="center">
      <a href="https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course" target="_blank">Qdrant</a>
    </td>
    <td align="center">
      <a href="https://github.com/superlinked/superlinked?utm_source=community&utm_medium=github&utm_campaign=oscourse" target="_blank">Superlinked</a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github" target="_blank">
        <img src="media/sponsors/comet.png" width="150" alt="Comet">
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/comet-ml/opik" target="_blank">
        <img src="media/sponsors/opik.svg" width="150" alt="Opik">
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/bytewax/bytewax?utm_source=github&utm_medium=decodingml&utm_campaign=2024_q1" target="_blank">
        <img src="media/sponsors/bytewax.png" width="150" alt="Bytewax">
      </a>
    </td>
    <td align="center">
      <a href="https://qdrant.tech/?utm_source=decodingml&utm_medium=referral&utm_campaign=llm-course" target="_blank">
        <img src="media/sponsors/qdrant.svg" width="150" alt="Qdrant">
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/superlinked/superlinked?utm_source=community&utm_medium=github&utm_campaign=oscourse" target="_blank">
        <img src="media/sponsors/superlinked.png" width="150" alt="Superlinked">
      </a>
    </td>
  </tr>
</table>

## Next steps

Our **LLM Engineer’s Handbook** inspired the **open-source LLM Twin course**.

Consider supporting our work by getting our book to **learn** a **complete framework** for **building and deploying production LLM & RAG systems** — from data to deployment.

Perfect for practitioners who want **both theory** and **hands-on** expertise by connecting the dots between DE, research, MLE and MLOps:

**[Buy the LLM Engineer’s Handbook](https://www.amazon.com/LLM-Engineers-Handbook-engineering-production/dp/1836200072/)**

* [On Amazon](https://www.amazon.com/LLM-Engineers-Handbook-engineering-production/dp/1836200072/)
* [On Packt](https://www.packtpub.com/en-us/product/llm-engineers-handbook-9781836200062)

![LLM Engineer's Handbook](media/llm_engineers_handbook_cover.png)
