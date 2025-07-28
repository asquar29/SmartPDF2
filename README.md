# 📘 PDF Section Extractor & Analyzer (Docker CLI)

This tool processes a folder of PDF files, extracts structured outlines, infers user intent (persona and task), and ranks the most relevant sections using semantic similarity.

It supports both direct PDF text extraction and OCR fallback. This version runs entirely in a **Docker container**, so no dependencies need to be installed locally.

---

## 🚀 Features

- Extracts section headings (H1, H2, H3) using font size and numbering
- Detects the document title
- Uses sentence embeddings to infer persona & rank top relevant sections
- OCR fallback via Tesseract for image-based PDFs
- CLI-enabled: accepts input/output paths
- Fully containerized with Docker

---

## 📦 Project Structure

project-folder/
├── main.py # Main Python script (CLI enabled)
├── requirements.txt # Python dependencies
├── Dockerfile # Docker build file
├── input/ # Place your PDFs here
└── output/ # Output JSON will be written here


---

## 🐳 Docker Setup

### 🔹 1. Build the Docker Image

Open terminal in the project directory and run:

```bash
docker build --platform=linux/amd64 -t pdf-extractor-cli:latest .


Run the Container
Make sure you have PDF files inside the input/ folder. Then run:


docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-extractor-cli:latest \
  --input_folder /app/input \
  --output /app/output/output.json
This mounts your local input/ and output/ folders into the container and runs the script.

Windows Users (CMD Prompt)

docker run --rm ^
  -v "%cd%/input:/app/input" ^
  -v "%cd%/output:/app/output" ^
  pdf-extractor-cli:latest ^
  --input_folder /app/input ^
  --output /app/output/output.json
📝 Output Example
json

{
  "metadata": {
    "persona": "Academic Researcher",
    "job": "Prepare literature review",
    "documents": ["example.pdf"],
    "timestamp": "2025-07-28T12:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "example.pdf",
      "page": 2,
      "section_title": "1.1 Related Work",
      "importance_score": 0.8432,
      "rank": 1
    }
    // ... up to 10 sections
  ],
  "subsection_analysis": [
    {
      "document": "example.pdf",
      "page": 2,
      "refined_text": "1.1 Related Work"
    }
  ]
}
📜 requirements.txt
Ensure you have the following dependencies in your requirements.txt:


pdfplumber
pdf2image
pytesseract
sentence-transformers
scikit-learn
numpy