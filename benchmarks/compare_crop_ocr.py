#!/usr/bin/env python3

import time
from pathlib import Path

import pymupdf
from rapidocr_onnxruntime import RapidOCR


PDF = Path(
    "electoral_roll_test/33112_200370__0009-00546.pdf"
)

SCALES = (2, 3)
GROUND_TRUTH = Path("benchmarks/ground_truth_crop.txt")
AI_IMAGE = Path("electoral_roll_text/ai_crop_x2.png")

def levenshtein(a, b):
    previous = list(range(len(b) + 1))

    for i, item_a in enumerate(a, start=1):
        current = [i]

        for j, item_b in enumerate(b, start=1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            substitute = previous[j - 1] + (item_a != item_b)

            current.append(min(insert, delete, substitute))

        previous = current

    return previous[-1]


def normalized_distance(reference, hypothesis):
    if not reference:
        return 0.0

    return levenshtein(reference, hypothesis) / len(reference)


def best_line_error(reference_line, ocr_lines):
    return min(
        normalized_distance(reference_line, line)
        for line in ocr_lines
    )


def run_ocr(pdf_path: Path, scale: int):
    ocr = RapidOCR()

    with pymupdf.open(pdf_path) as doc:
        page = doc[0]

        crop = pymupdf.Rect(
            0,
            0,
            page.rect.width,
            page.rect.height / 5,
        )

        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(scale, scale),
            clip=crop,
            alpha=False,
        )

        start = time.perf_counter()
        result, _ = ocr(pix.tobytes("png"))
        elapsed = time.perf_counter() - start

    lines = [item[1] for item in result or []]

    return lines, elapsed
    
def run_ai_ocr(image_path: Path):
    ocr = RapidOCR()

    start = time.perf_counter()
    result, _ = ocr(str(image_path))
    elapsed = time.perf_counter() - start

    lines = [item[1] for item in result or []]

    return lines, elapsed

def main():
    reference = GROUND_TRUTH.read_text(encoding="utf-8").strip()
    for scale in SCALES:
        lines, elapsed = run_ocr(PDF, scale)
#        hypothesis = "\n".join(lines)

#        cer = character_error_rate(reference, hypothesis)
#        wer = word_error_rate(reference, hypothesis)
        reference_lines = reference.splitlines()

        errors = [
            best_line_error(reference_line, lines)
            for reference_line in reference_lines
            if reference_line.strip()
        ]

        mean_line_error = sum(errors) / len(errors)
        print(f"\n=== RapidOCR {scale}x ===")
        print(f"Detected lines : {len(lines)}")
        print(f"OCR time       : {elapsed:.2f} s")
#        print(f"CER            : {cer:.3f}")
#        print(f"WER            : {wer:.3f}")
        print(f"Mean line error: {mean_line_error:.3f}")
        matches = [
            line for line in lines
            if "stanley" in line.lower()
        ]

        print("Stanley matches:")
        for line in matches:
            print(f"  {line}")

    lines, elapsed = run_ai_ocr(AI_IMAGE)

    reference_lines = reference.splitlines()

    errors = [
        best_line_error(reference_line, lines)
        for reference_line in reference_lines
        if reference_line.strip()
    ]

    mean_line_error = sum(errors) / len(errors)

    print("\n=== AI-enhanced x2 ===")
    print(f"Detected lines : {len(lines)}")
    print(f"OCR time       : {elapsed:.2f} s")
    print(f"Mean line error: {mean_line_error:.3f}")
    
if __name__ == "__main__":
    main()