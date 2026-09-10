#!/usr/bin/env python3

import argparse
import logging
import multiprocessing as mp
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
from pypdf import PdfReader
from tqdm import tqdm


MIN_TEXT_THRESHOLD = 50
LOG_FILE = "pdf_processing.log"


# ==========================================================
# Logging Setup
# ==========================================================

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(processName)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ==========================================================
# Extraction Engines
# ==========================================================

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
        logging.info(f"Fallback triggered: {pdf_path}")
        text = extract_with_pypdf(pdf_path)

    return text


# ==========================================================
# Worker Function (Multiprocessing)
# ==========================================================

def process_file(args):
    pdf_path, input_root, output_root, overwrite, skip_existing = args

    try:
        relative = pdf_path.relative_to(input_root)
        output_file = output_root / relative.with_suffix(".txt")

        if skip_existing and output_file.exists():
            return "skipped"

        if output_file.exists() and not overwrite:
            return "skipped"

        text = extract_text(pdf_path)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(text, encoding="utf-8")

        return "success"

    except Exception as e:
        logging.error(f"Failed {pdf_path}: {e}")
        return "failed"


# ==========================================================
# Processing Engine
# ==========================================================

def process_directory(input_dir, output_dir, workers, overwrite, skip_existing):
    start_time = time.time()

    pdf_files = list(input_dir.rglob("*.pdf"))
    total = len(pdf_files)

    if total == 0:
        print("No PDF files found.")
        return

    print(f"Found {total} PDF files.")
    print(f"Using {workers} worker(s).\n")

    args = [
        (pdf, input_dir, output_dir, overwrite, skip_existing)
        for pdf in pdf_files
    ]

    results = {"success": 0, "failed": 0, "skipped": 0}

    with mp.Pool(processes=workers) as pool:
        for result in tqdm(pool.imap_unordered(process_file, args), total=total):
            results[result] += 1

    duration = time.time() - start_time

    print("\n========= SUMMARY =========")
    print(f"Total Files : {total}")
    print(f"Success     : {results['success']}")
    print(f"Skipped     : {results['skipped']}")
    print(f"Failed      : {results['failed']}")
    print(f"Time Taken  : {duration:.2f} seconds")
    print("===========================\n")


# ==========================================================
# Interactive Mode
# ==========================================================

def interactive_mode():
    print("\n=== Enterprise PDF to Text Converter ===\n")

    input_dir = Path(input("Enter input directory: ").strip().strip('"'))
    output_dir = Path(input("Enter output directory: ").strip().strip('"'))

    if not input_dir.exists() or not input_dir.is_dir():
        print("Invalid input directory.")
        sys.exit(1)

    if not output_dir.exists():
        create = input("Output directory doesn't exist. Create it? (y/n): ").lower()
        if create == "y":
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            sys.exit(0)

    workers = int(input(f"Number of workers (default {mp.cpu_count()}): ") or mp.cpu_count())

    process_directory(input_dir, output_dir, workers, overwrite=False, skip_existing=True)


# ==========================================================
# CLI Entry
# ==========================================================

def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="Enterprise PDF to Text Converter")

    parser.add_argument("--input", help="Input directory")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--workers", type=int, default=mp.cpu_count())
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--interactive", action="store_true")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print("Input directory does not exist.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    process_directory(
        input_dir,
        output_dir,
        args.workers,
        args.overwrite,
        args.skip_existing,
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()