# Text Generation API

This API allows you to generate text using different AI models. It supports multiple providers and models, including OpenAI and Groq.

## Features

- **Generate Text**: Generate text based on a given prompt using specified AI models.
- **Flexible Configuration**: Configure the provider, model, prompt, and other parameters for text generation.

## Installation

To run this application, you need Python installed along with the required libraries. You can install the dependencies using the following command:

```sh
pip install -r requirements.txt
```

## How to Use

### 1. Generate Text

Send a POST request to the `/generate-text` endpoint with the required parameters.

### Request Body

- `provider`: The text generation service provider, e.g., 'groq' or 'openai'.
- `model`: The model identifier, specifying which language model to use for text generation.
- `prompt`: The input prompt for the language model.
- `temperature`: Controls the randomness of the output. Lower values make it more predictable.
- `return_prompt`: A boolean flag to specify whether to return the original prompt with the generated text.
- `max_tokens`: The maximum number of tokens to generate. Default is 4000.
- `system_instructions`: Instructions that define the context or constraints for the model.

### Example Request

```json
{
    "provider": "openai",
    "model": "gpt4",
    "prompt": "Write a story about a brave knight.",
    "temperature": 0.7,
    "return_prompt": true,
    "max_tokens": 200,
    "system_instructions": "You are a creative writer"
}
```

### Example Response

```json
{
    "generated_text": "Once upon a time...",
    "input_token": 10,
    "output_token": 50,
    "prompt_returned": "Write a story about a brave knight."
}
```

## API Endpoints

### `POST /generate-text`

Generates text based on the provided prompt and parameters.

#### Request Body

```json
{
    "provider": "string",
    "model": "string",
    "prompt": "string",
    "temperature": "float",
    "return_prompt": "boolean",
    "max_tokens": "integer",
    "system_instructions": "string"
}
```

#### Response

```json
{
    "generated_text": "string",
    "input_token": "integer",
    "output_token": "integer",
    "prompt_returned": "string"
}
```

## Contributing

If you want to help improve this project, please fork the repository and submit a pull request. We welcome all improvements and fixes.

## License

This project is licensed under the MIT License.
