# PDF Intelligence Service

This project is a PDF intelligence service created for the Adobe Hackathon - Challenge 1A. It analyzes PDF documents to extract structural information, such as titles and hierarchical headings (H1, H2, H3), and outputs the results in a structured JSON format.

## Features

- **PDF Text Extraction**: Extracts all text from PDF documents.
- **Title Detection**: Automatically identifies the main title of the document.
- **Heading Detection**: Detects hierarchical headings (H1, H2, H3) based on font size, style, and numeric prefixes.
- **JSON Output**: Outputs the extracted document structure in a clean, easy-to-use JSON format.
- **Batch Processing**: Can process multiple PDF files from an input directory.

## Requirements

- Python 3.11+
- Poetry
- Docker (optional)

## How to Run

### Using Poetry (Recommended)

1.  **Install Poetry**:
    ```bash
    pip install poetry
    ```

2.  **Install Dependencies**:
    Navigate to the project directory and run:
    ```bash
    poetry install
    ```

3.  **Run the Application**:
    ```bash
    poetry run python -m app.main
    ```

    Alternatively, you can use the provided batch file on Windows:
    ```bash
    run_poetry.bat
    ```

### Using Docker

1.  **Build the Docker Image**:
    ```bash
    docker build -t pdf-processor-1a .
    ```

2.  **Run the Docker Container**:
    Make sure you have your PDF files in an `input` directory. The output will be saved to an `output` directory.

    ```bash
    docker run --rm -v "$(pwd)/input:/app/input:ro" -v "$(pwd)/output:/app/output" --network none pdf-processor-1a
    ```

    For Windows Command Prompt:
    ```bash
    docker run --rm -v "%cd%\\input:/app/input:ro" -v "%cd%\\output:/app/output" --network none pdf-processor-1a
    ```

## Project Structure

```
Adobe-India-Hackathon25-Challenge1a/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main application logic
│   ├── models/
│   │   └── documents.py        # Pydantic models for document structure
│   └── services/
│       └── heading_detector.py # Core logic for heading detection
├── input/
│   └── (place your PDF files here)
├── output/
│   └── (JSON output will be saved here)
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── README.md
```
