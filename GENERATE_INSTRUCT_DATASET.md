# Generate Data for LLM finetuning task component

## Component Structure

### File Handling
- `file_handler.py`: Manages file I/O operations, enabling reading and writing of JSON formatted data.

### LLM Communication
- `llm_communication.py`: Handles communication with OpenAI's LLMs, sending prompts and processing responses.

### Data Generation
- `generate_data.py`: Orchestrates the generation of training data by integrating file handling, LLM communication, and data formatting.


### Usage

The project includes a `Makefile` for easy management of common tasks. Here are the main commands you can use:

- `make help`: Displays help for each make command.
- `make local-start`: Build and start mongodb, mq and qdrant.
- `make local-test-github`: Insert data to mongodb
- `make generate-dataset`: Generate dataset for finetuning and version it in CometML