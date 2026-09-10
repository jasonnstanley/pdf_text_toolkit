#!/usr/bin/env python3

from pathlib import Path
import time

import numpy as np
import pymupdf
import torch
from PIL import Image
from spandrel import ModelLoader


PDF = Path(
    "electoral_roll_test/33112_200370__0009-00546.pdf"
)

MODEL = Path(
    "models/RealESRGAN_x2plus.pth"
)

OUTPUT = Path(
    "electoral_roll_text/ai_crop_x2.png"
)


def pixmap_to_tensor(pix):
    image = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples,
    )

    array = np.asarray(image).astype("float32") / 255.0

    tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)

    return tensor


def tensor_to_image(tensor):
    array = (
        tensor.squeeze(0)
        .permute(1, 2, 0)
        .clamp(0, 1)
        .cpu()
        .numpy()
    )

    array = (array * 255).astype("uint8")

    return Image.fromarray(array)


def main():
    print("=== AI Crop Enhancement Test ===")

    model = ModelLoader().load_from_file(MODEL)
    model.eval()

    with pymupdf.open(PDF) as doc:
        page = doc[0]

        crop = pymupdf.Rect(
            0,
            0,
            page.rect.width,
            page.rect.height / 5,
        )

        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            clip=crop,
            alpha=False,
        )

    print(f"Input crop : {pix.width} x {pix.height}")

    x = pixmap_to_tensor(pix)

    start = time.perf_counter()

    with torch.inference_mode():
        y = model(x)

    elapsed = time.perf_counter() - start

    image = tensor_to_image(y)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)

    print(f"Output     : {image.width} x {image.height}")
    print(f"Time       : {elapsed:.2f} s")
    print(f"Saved      : {OUTPUT}")


if __name__ == "__main__":
    main()