#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import pymupdf as fitz  # PyMuPDF
from pypdf import PdfReader
from tqdm import tqdm
import sys

MIN_TEXT_THRESHOLD = 50
LOG_FILE = "pdf_processing.log"

# =========================
# Logging Setup
# =========================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# =========================
# Extraction Engines
# =========================

def extract_with_pymupdf(pdf_path: Path) -> str:
    text_chunks = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_chunks.append(page.get_text("text"))
    return "\n".join(text_chunks)


def extract_with_pypdf(pdf_path: Path) -> str:
    text = ""
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text


def extract_text(pdf_path: Path) -> str:
    text = extract_with_pymupdf(pdf_path)

    if len(text.strip()) < MIN_TEXT_THRESHOLD:
        logging.info(f"Fallback to pypdf: {pdf_path}")
        text = extract_with_pypdf(pdf_path)

    return text


# =========================
# Directory Processing
# =========================

def process_directory(input_dir: Path, output_dir: Path):
    if not input_dir.exists():
        print("Error: Input directory does not exist.")
        sys.exit(1)

    if not input_dir.is_dir():
        print("Error: Input path must be a directory.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.rglob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            text = extract_text(pdf_file)

            relative_path = pdf_file.relative_to(input_dir)
            output_file = output_dir / relative_path.with_suffix(".txt")
            output_file.parent.mkdir(parents=True, exist_ok=True)

            output_file.write_text(text, encoding="utf-8")

        except Exception as e:
            logging.error(f"Failed {pdf_file}: {e}")

    print("Processing complete.")


# =========================
# CLI Entry
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="Recursively convert PDFs in a directory to text files."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input directory containing PDF files",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output directory for text files",
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()
