#!/usr/bin/env python3

import time
from pathlib import Path

import pymupdf
from rapidocr_onnxruntime import RapidOCR


PDF = Path(
    "electoral_roll_test/33112_200370__0009-00546.pdf"
)

SCALES = (2, 3)


def run_ocr(pdf_path: Path, scale: int):
    ocr = RapidOCR()

    with pymupdf.open(pdf_path) as doc:
        page = doc[0]
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(scale, scale),
            alpha=False,
        )

        start = time.perf_counter()
        result, _ = ocr(pix.tobytes("png"))
        elapsed = time.perf_counter() - start

    lines = [item[1] for item in result or []]

    return lines, elapsed


def main():
    for scale in SCALES:
        lines, elapsed = run_ocr(PDF, scale)

        print(f"\n=== RapidOCR {scale}x ===")
        print(f"Detected lines : {len(lines)}")
        print(f"OCR time       : {elapsed:.2f} s")

        matches = [
            line for line in lines
            if "stanley" in line.lower()
        ]

        print("Stanley matches:")
        for line in matches:
            print(f"  {line}")


if __name__ == "__main__":
    main()