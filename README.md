# PRD Generator and Enhancer

Welcome to the PRD Generator and Enhancer! This tool helps you create, improve, and brainstorm Product Requirement Documents (PRDs) using AI. It's designed to make your work easier and more efficient.

## Features

- **Create New PRD**: Make a new Product Requirement Document from scratch.
- **Improve Current PRD**: Make your existing PRD better.
- **Brainstorm Features**: Get new ideas for your product.
- **Generate Tracking Plan**: Create a detailed plan to track product features and details.
- **View History**: Look back at all your interactions and documents.

## Installation

To use this app, you need Python installed on your computer. Install the required libraries with this command:

```sh
pip install -r requirements.txt
```

## How to Use

### 1. Create New PRD

1. **Enter Product Details**: Type in your product's name and description.
2. **Generate PRD**: Click "Generate PRD" to create your document.
3. **Review and Adjust**: The AI will draft the document, review it, and make improvements.
4. **Download PRD**: Download the final PRD as a Markdown file.

### 2. Improve Current PRD

1. **Paste Existing PRD**: Enter your current PRD text.
2. **Improve PRD**: Click "Improve PRD" to enhance it.
3. **Review and Adjust**: The AI will suggest improvements and make changes.
4. **Download Improved PRD**: Download the improved PRD as a Markdown file.

### 3. Brainstorm Features

1. **Start Brainstorming**: Enter your topic or question.
2. **Interactive Session**: Chat with the AI to get ideas.
3. **Review Suggestions**: Look at and refine the AI's suggestions.

### 4. Generate Tracking Plan

1. **Enter Feature Details**: Provide the feature name, customer type, and other details.
2. **Generate Plan**: Click "Generate Tracking" to create your plan.
3. **Review and Adjust**: The AI will draft the plan and suggest improvements.
4. **Download Plan**: Download the tracking plan as a Markdown file.

### 5. View History

1. **View All Interactions**: See all your past interactions and documents.

## Code Overview

```python
import streamlit as st
from utils import download_audio
from models import transcribe_audio

def create_prd(system_prompt_prd, system_prompt_director, llm_model, fast_llm_model):
    # Function to create a new PRD
    ...

def improve_prd(system_prompt_prd, system_prompt_director, llm_model):
    # Function to improve an existing PRD
    ...

def brainstorm_features(system_prompt_brainstorm, llm_model):
    # Function to brainstorm new features or ideas
    ...

def view_history():
    # Function to view history of interactions and documents
    ...

def tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, llm_model):
    # Function to create a tracking plan
    ...

```

## Contributing

If you want to help improve this project, please fork the repository and submit a pull request. We welcome all improvements and fixes.

## License

This project is licensed under the MIT License.
