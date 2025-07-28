import os
import re
import json
import argparse
import numpy as np
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# ---------------- CONFIG ----------------
DEFAULT_POPPLER_PATH = r"C:\Users\htc\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 10

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# ---------------- Helper Functions ----------------
def clean_text(text):
    text = re.sub(r'\.{2,}', '', text)
    text = re.sub(r'\s+\d+$', '', text)
    return text.strip()

def detect_numbering_level(text):
    match = re.match(r'^\d+(\.\d+)*', text.strip())
    if not match:
        return None
    depth = text.count(".") + 1
    return "H1" if depth == 1 else "H2" if depth == 2 else "H3"

def extract_outline_from_pdf(pdf_path, poppler_path):
    print(f"Processing: {pdf_path}")
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    all_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            lines_dict = defaultdict(list)
            for char in page.chars:
                top = round(char["top"] / 2) * 2
                lines_dict[top].append(char)

            for top in sorted(lines_dict.keys()):
                line_chars = sorted(lines_dict[top], key=lambda c: c["x0"])
                line_text = "".join(c["text"] for c in line_chars).strip()
                if line_text:
                    font_sizes = [c["size"] for c in line_chars]
                    avg_font_size = round(sum(font_sizes) / len(font_sizes), 2)
                    all_lines.append({
                        "text": line_text,
                        "font_size": avg_font_size,
                        "page": page_number
                    })

    unique_sizes = sorted({line["font_size"] for line in all_lines}, reverse=True)
    font_to_heading = {}
    if len(unique_sizes) > 0: font_to_heading[unique_sizes[0]] = "Title"
    if len(unique_sizes) > 1: font_to_heading[unique_sizes[1]] = "H1"
    if len(unique_sizes) > 2: font_to_heading[unique_sizes[2]] = "H2"
    if len(unique_sizes) > 3: font_to_heading[unique_sizes[3]] = "H3"

    title = " ".join([l["text"] for l in all_lines if l["font_size"] == unique_sizes[0]]).strip()

    outline = []
    seen = set()
    for line in all_lines:
        text = clean_text(line["text"])
        if len(text.split()) > 15:
            continue
        level = detect_numbering_level(text) or font_to_heading.get(line["font_size"])
        if level in {"H1", "H2", "H3"} and text not in seen:
            outline.append({"level": level, "text": text, "page": line["page"]})
            seen.add(text)

    return {"title": title, "outline": outline}

def infer_persona_and_job(documents):
    combined_text = " ".join([doc["title"] for doc in documents])
    if "travel" in combined_text.lower() or "destination" in combined_text.lower():
        return "Travel Planner", "Create a travel itinerary"
    if "finance" in combined_text.lower() or "investment" in combined_text.lower():
        return "Financial Analyst", "Summarize financial report"
    if "research" in combined_text.lower():
        return "Academic Researcher", "Prepare literature review"
    return "General Analyst", "Summarize key points"

def compute_similarity(query, texts):
    query_emb = model.encode([query], convert_to_tensor=False)
    text_embs = model.encode(texts, convert_to_tensor=False)
    return cosine_similarity(query_emb, text_embs)[0]

# ---------------- Main Pipeline ----------------
def process_folder(pdf_folder, output_path, poppler_path=DEFAULT_POPPLER_PATH):
    documents = []
    for file in os.listdir(pdf_folder):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, file)
            doc = extract_outline_from_pdf(pdf_path, poppler_path)
            doc["source"] = file
            documents.append(doc)

    persona, job = infer_persona_and_job(documents)
    query = f"Persona: {persona}. Task: {job}."

    sections = []
    for doc in documents:
        for item in doc["outline"]:
            sections.append({
                "document": doc["source"],
                "page": item["page"],
                "text": item["text"]
            })

    if not sections:
        print("No sections found.")
        return

    section_texts = [s["text"] for s in sections]
    scores = compute_similarity(query, section_texts)
    ranked_indices = np.argsort(scores)[::-1]

    top_sections = []
    for rank, idx in enumerate(ranked_indices[:TOP_K], start=1):
        s = sections[idx]
        top_sections.append({
            "document": s["document"],
            "page": s["page"],
            "section_title": s["text"],
            "importance_score": round(float(scores[idx]), 4),
            "rank": rank
        })

    result = {
        "metadata": {
            "persona": persona,
            "job": job,
            "documents": [d["source"] for d in documents],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "extracted_sections": top_sections,
        "subsection_analysis": [
            {
                "document": s["document"],
                "page": s["page"],
                "refined_text": s["text"]
            } for s in top_sections
        ]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Persona: {persona}")
    print(f"Job: {job}")
    print(f"Output saved to {output_path}")

# ---------------- CLI Entry ----------------
def main():
    parser = argparse.ArgumentParser(description="PDF Section Extractor & Analyzer")
    parser.add_argument(
        "--input_folder",
        type=str,
        required=True,
        help="Path to folder containing PDF files"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to save the output JSON"
    )
    parser.add_argument(
        "--poppler_path",
        type=str,
        default=DEFAULT_POPPLER_PATH,
        help="Path to poppler binaries (default is Windows path)"
    )

    args = parser.parse_args()
    process_folder(args.input_folder, args.output, args.poppler_path)

if __name__ == "__main__":
    main()
