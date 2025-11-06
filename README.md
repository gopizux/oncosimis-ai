# Oncosimis AI Assistant

This project is an AI-powered chatbot for Oncosimis Biotech, designed to answer questions about the company, its technology platforms, and provide access to Standard Operating Procedures (SOPs).

## About The Project

The Oncosimis AI Assistant is a web-based chatbot that leverages a local large language model (LLM) to provide information to users. It has a simple and intuitive interface for users to interact with the AI, and a backend that serves the AI model and documents.

### Features

*   **AI-Powered Chat**: Utilizes a local LLM (Ollama with llama2:7b) to answer user queries.
*   **Company Knowledge Base**: Pre-loaded with information about Oncosimis Biotech, its mission, team, and proprietary technologies (AcceTT® and BacSec®).
*   **SOP Document Access**: Allows users to list and download Standard Operating Procedure documents.
*   **Web Interface**: A clean and user-friendly chat interface built with HTML, CSS, and JavaScript.
*   **FastAPI Backend**: A robust backend built with Python and FastAPI to handle chat logic, document serving, and AI model interaction.
*   **Standalone Landing Page**: Includes a premium, modern landing page (`premium_oncosimis.html`) with a non-functional chat widget, which can be integrated with the chatbot.

## Tech Stack

*   **Backend**:
    *   Python
    *   FastAPI
    *   Ollama
    *   `llama2:7b` model
    *   Uvicorn
*   **Frontend**:
    *   HTML
    *   CSS
    *   JavaScript
*   **SOP Documents**:
    *   Microsoft Word (`.docx`)

## Project Structure

```
.
├── backend/
│   ├── app.py              # FastAPI application
│   ├── document_loader.py  # Logic for loading SOP documents
│   ├── requirements.txt    # Python dependencies
│   └── ...
├── frontend/
│   ├── index.html          # Main chat interface
│   ├── script.js           # Frontend JavaScript logic
│   ├── style.css           # Styles for the chat interface
│   └── assets/
│       └── ...
├── SOPs-feed/
│   ├── ...                 # Directory for SOP .docx files
├── premium_oncosimis.html  # Standalone landing page
└── README.md
```

## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

*   **Python 3.7+**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
*   **Ollama**: You need to have Ollama installed and running.
    *   [https://ollama.ai/](https://ollama.ai/)
*   **LLM Model**: Pull the `llama2:7b` model:
    ```sh
    ollama pull llama2:7b
    ```

### Installation & Running

1.  **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd oncosimis-ai
    ```

2.  **Backend Setup**:
    *   Navigate to the `backend` directory:
        ```sh
        cd backend
        ```
    *   Create and activate a virtual environment:
        ```sh
        python -m venv venv
        source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
        ```
    *   Install the required Python packages:
        ```sh
        pip install -r requirements.txt
        ```
    *   Start the backend server:
        ```sh
        uvicorn app:app --reload
        ```
    The backend will be running at `http://localhost:8000`.

3.  **Frontend Setup**:
    *   Open the `frontend/index.html` file in your web browser.
    *   Alternatively, you can serve the `frontend` directory using a simple HTTP server. For example, with Python:
        ```sh
        cd frontend
        python -m http.server
        ```
        The frontend will be accessible at `http://localhost:8000` (or another port if 8000 is in use).

## Usage

1.  **Chat Interface**:
    *   Open the `frontend/index.html` file in your browser.
    *   The chat interface will connect to the backend automatically.
    *   You can ask questions about Oncosimis, its technologies, or request SOPs.

2.  **Standalone Landing Page**:
    *   Open `premium_oncosimis.html` in your browser to see the company's landing page.
    *   The chat widget on this page is currently a placeholder and needs to be integrated with the chatbot functionality.