#!/usr/bin/env python3

import time
from pathlib import Path

import pymupdf
from rapidocr_onnxruntime import RapidOCR
import csv

PDF = Path(
    "electoral_roll_test/33112_200370__0009-00546.pdf"
)

SCALES = (2, 3)
#GROUND_TRUTH = Path("benchmarks/ground_truth/crop_01.txt")
CROPS = [
    {
        "name": "crop_01",
        "start": 0 / 5,
        "end": 1 / 5,
        "ground_truth": Path("benchmarks/ground_truth/crop_01.txt"),
    },
    {
        "name": "crop_02",
        "start": 2 / 5,
        "end": 3 / 5,
        "ground_truth": Path("benchmarks/ground_truth/crop_02.txt"),
    },
]
AI_IMAGE = Path("electoral_roll_text/ai_crop_x2.png")
RESULTS_FILE = Path("benchmarks/results/ocr_benchmark_latest.csv")
TIMING_FILE = Path(
    "benchmarks/results/ai_enhancement_timing.txt"
)

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


def run_ocr(pdf_path: Path, scale: int, start_fraction: float, end_fraction: float):
    
    ocr = RapidOCR()

    with pymupdf.open(pdf_path) as doc:
        page = doc[0]

        crop = pymupdf.Rect(
            0,
            page.rect.height * start_fraction,
            page.rect.width,
            page.rect.height * end_fraction,
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
    results_rows = []

    for crop in CROPS:
        reference = crop["ground_truth"].read_text(
            encoding="utf-8"
        ).strip()

        print(f"\n##### {crop['name']} #####")

        for scale in SCALES:
            lines, elapsed = run_ocr(
                PDF,
                scale,
                crop["start"],
                crop["end"],
            )

            reference_lines = reference.splitlines()

            errors = [
                best_line_error(reference_line, lines)
                for reference_line in reference_lines
                if reference_line.strip()
            ]

            mean_line_error = sum(errors) / len(errors)

            results_rows.append({
                "crop": crop["name"],
                "method": "RapidOCR",
                "render_scale": scale,
                "detected_lines": len(lines),
                "ocr_time_seconds": round(elapsed, 2),
                "mean_line_error": round(mean_line_error, 3),
                "enhancement_time_seconds": 0.00,
                "total_time_seconds": round(elapsed, 2),
            })

            print(f"\n=== RapidOCR {scale}x ===")
            print(f"Detected lines : {len(lines)}")
            print(f"OCR time       : {elapsed:.2f} s")
            print(f"Mean line error: {mean_line_error:.3f}")

        if crop["name"] == "crop_01":
            lines, elapsed = run_ai_ocr(AI_IMAGE)

            reference_lines = reference.splitlines()

            errors = [
                best_line_error(reference_line, lines)
                for reference_line in reference_lines
                if reference_line.strip()
            ]

            mean_line_error = sum(errors) / len(errors)

            enhancement_time = float(
                TIMING_FILE.read_text(
                    encoding="utf-8"
                ).strip()
            )

            results_rows.append({
                "crop": crop["name"],
                "method": "RealESRGAN_x2plus+RapidOCR",
                "render_scale": 2,
                "detected_lines": len(lines),
                "ocr_time_seconds": round(elapsed, 2),
                "mean_line_error": round(mean_line_error, 3),
                "enhancement_time_seconds": enhancement_time,
                "total_time_seconds": round(
                    elapsed + enhancement_time, 2
                ),
            })

            print("\n=== AI-enhanced x2 ===")
            print(f"Detected lines : {len(lines)}")
            print(f"OCR time       : {elapsed:.2f} s")
            print(f"Mean line error: {mean_line_error:.3f}")

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "crop",
                "method",
                "render_scale",
                "detected_lines",
                "ocr_time_seconds",
                "mean_line_error",
                "enhancement_time_seconds",
                "total_time_seconds",
            ],
        )

        writer.writeheader()
        writer.writerows(results_rows)

    print(f"\nResults saved   : {RESULTS_FILE}")
    
if __name__ == "__main__":
    main()