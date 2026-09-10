#!/usr/bin/env python3

from pathlib import Path

import pymupdf
import torch


PDF = Path(
    "electoral_roll_test/33112_200370__0009-00546.pdf"
)


def main():
    print("=== AI Enhancement Benchmark ===")
    print(f"PDF     : {PDF}")
    print(f"PyTorch : {torch.__version__}")
    print(f"Device  : {'cuda' if torch.cuda.is_available() else 'cpu'}")

    with pymupdf.open(PDF) as doc:
        page = doc[0]
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            alpha=False,
        )

    print(f"Input   : {pix.width} x {pix.height}")
    print("Ready for learned enhancement model.")


if __name__ == "__main__":
    main()