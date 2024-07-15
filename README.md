# PM Toolkit

PM Toolkit is a comprehensive Streamlit application designed to assist Product Managers with various tasks, including creating and improving Product Requirements Documents (PRDs), brainstorming features, generating tracking plans, creating Go-To-Market (GTM) plans, and analyzing A/B/C test results.

## Features

1. **Create PRD**: Generate a new Product Requirements Document using AI.
2. **Improve PRD**: Enhance an existing PRD with AI-powered suggestions.
3. **Brainstorm Features**: Engage in an interactive brainstorming session for new product features.
4. **Tracking Plan**: Generate a detailed tracking plan for your product or feature.
5. **Create GTM Plan**: Develop a Go-To-Market plan based on your PRD and additional details.
6. **A/B/C Test Significance**: Analyze and interpret the results of A/B/C tests.
7. **View History**: Access and review previously generated PRDs and plans.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd pm-toolkit
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the necessary environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GROQ_API_KEY`: Your Groq API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase API key
   - `SUPABASE_TABLE`: Your Supabase table name for storing PRDs
   - `SUPABASE_BRAINTORM_TABLE`: Your Supabase table name for storing brainstorming sessions

## Usage

Run the Streamlit app:

```
streamlit run chatprd.py
```

Navigate through the sidebar to access different features of the PM Toolkit.

## Project Structure

- `chatprd.py`: Main Streamlit application entry point
- `features.py`: Contains implementations for various features (Create PRD, Improve PRD, etc.)
- `models.py`: Handles the initialization and configuration of AI models
- `storage.py`: Manages database operations with Supabase
- `utils.py`: Utility functions for data loading, audio processing, etc.
- `api/llm/`: Contains wrappers for different AI models (OpenAI, Groq, Anthropic)
- `prompts.json`: Stores system prompts for different features

## Dependencies

- streamlit
- openai
- pandas
- numpy
- scipy
- llm
- groq
- Pillow
- anthropic
- ffmpeg
- yt-dlp
- supabase
- PyJWT
- streamlit-cookies-controller
- extra-streamlit-components

## Authentication

The app uses Supabase for user authentication. Users need to log in before accessing the toolkit features.

## AI Models

The toolkit uses multiple AI models for different tasks:
- OpenAI's GPT-4
- Groq's LLaMA 3 70B
- Anthropic's Claude 3.5 Sonnet

## Contributing

Contributions to the PM Toolkit are welcome. Please ensure to follow the existing code style and add unit tests for any new features.

## License

[Add your license information here]

## Support

For any issues or feature requests, please open an issue on the GitHub repository.