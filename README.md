PDF Section Extractor & Analyzer
This Python CLI tool processes a folder of PDFs, extracts structured section outlines using font and numbering heuristics, and ranks the most relevant sections based on inferred persona and task using embeddings.

It leverages:

pdfplumber for text extraction

pdf2image and poppler for image conversion

pytesseract for OCR fallback

sentence-transformers for semantic similarity

📂 Folder Structure


.
├── main.py               # Main CLI Python script
├── requirements.txt      # Dependencies
├── README.md             # This file
├── input/                # Put your input PDFs here (optional if using CLI)
└── output.json           # Output file path as set by CLI
🛠️ Features
📑 Extracts titles and hierarchical section headings (H1, H2, H3)

📈 Infers persona and task from document content

🤖 Uses sentence embeddings to rank the top 10 most relevant sections

🔍 Supports both PDF parsing and OCR fallback

🧠 CLI interface to allow flexible usage

💻 Installation
Install system dependencies (Linux/macOS):


sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
On Windows, download and install:

Poppler for Windows

Tesseract OCR for Windows

Clone the repo and install Python dependencies:


pip install -r requirements.txt
📦 requirements.txt
txt

pdfplumber
pdf2image
pytesseract
sentence-transformers
scikit-learn
numpy
🚀 Usage
🔹 Command-Line Execution

python main.py \
  --input_folder "path/to/folder/with/pdfs" \
  --output "output.json"
🔹 Optional: Custom Poppler Path (Windows only)

python main.py \
  --input_folder "path/to/pdfs" \
  --output "output.json" \
  --poppler_path "C:/path/to/poppler/bin"
📤 Output Format
Example output.json:


{
  "metadata": {
    "persona": "Academic Researcher",
    "job": "Prepare literature review",
    "documents": ["file1.pdf", "file2.pdf"],
    "timestamp": "2025-07-28T10:22:43.123Z"
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "page": 3,
      "section_title": "1.1 Related Work",
      "importance_score": 0.8423,
      "rank": 1
    }
    // ... up to TOP_K (10)
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "page": 3,
      "refined_text": "1.1 Related Work"
    }
  ]
}
🧠 How It Works
Step	Description
1️⃣	Extracts text from PDFs page-by-page using pdfplumber
2️⃣	Detects section headers using font size and numbering
3️⃣	Infers "persona" (e.g., Researcher, Financial Analyst) from content
4️⃣	Uses Sentence-BERT to find the most relevant sections for the inferred task
5️⃣	Saves a ranked list of important sections with metadata in a JSON

👤 Persona Detection Logic
Based on keywords in document titles:

Keyword	Persona	Task
travel	Travel Planner	Create a travel itinerary
finance	Financial Analyst	Summarize financial report
research	Academic Researcher	Prepare literature review
(default)	General Analyst	Summarize key points

📎 Example

python main.py \
  --input_folder "C:\Users\htc\Documents\PDFs" \
  --output "output_1B.json"