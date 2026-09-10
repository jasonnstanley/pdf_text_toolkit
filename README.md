# PDF Text Toolkit

A reproducible Python toolkit for extracting text from PDFs, recovering text from scanned documents with OCR, and experimentally evaluating image-enhancement strategies for difficult historical source material.

The project began from the `frankcasas/PDF-to-Text` recursive PDF extraction utility and has since developed into a broader OCR and document-analysis toolkit.

## Current Capabilities

- Recursive PDF-to-text conversion
- Preserved input directory structure
- Native text extraction with PyMuPDF
- Automatic fallback to pypdf
- Automatic OCR fallback for image-only PDFs
- RapidOCR / ONNX Runtime OCR
- Configurable high-resolution PDF rendering
- JPG-to-PDF ingestion utility
- PyTorch-based learned image enhancement experiments
- RealESRGAN x2 enhancement through Spandrel
- Human-verified OCR ground-truth samples
- Multi-crop OCR benchmarking
- Content-aware OCR error measurement
- Automated benchmark CSV generation
- Processing-time measurement
- Python syntax, AST and loop-structure checking
- Reproducible Python environment
- Cross-platform project structure

## Project Structure

```text
pdf_text_toolkit/
├── benchmarks/
│   ├── ground_truth/
│   ├── results/
│   ├── compare_ai_enhancement.py
│   ├── compare_crop_ocr.py
│   └── compare_ocr.py
├── scripts/
│   ├── check_python.py
│   ├── jpg_to_pdf_batch.py
│   ├── pdf_to_text.py
│   └── pdf_to_text_enterprise.py
├── models/                 # local pretrained weights; not committed
├── requirements.txt
└── README.md
```
Private source documents, generated OCR output, virtual environments and pretrained model weights are excluded from version control.

## Extraction Pipeline

The main converter uses a staged fallback strategy:
```text
PDF
 │
 ├─ PyMuPDF text extraction
 │
 ├─ pypdf fallback
 │
 └─ RapidOCR fallback
       │
       └─ rendered PDF page → image → OCR → UTF-8 text
```
This allows the same workflow to process both digitally generated PDFs and image-only scanned documents.

## OCR Benchmarking

The toolkit includes an experimental framework for comparing OCR strategies against manually verified ground truth.

Current benchmark methods include:

```text
PDF scan
 ├─ 2× render → RapidOCR
 ├─ 3× render → RapidOCR
 └─ 2× render → RealESRGAN x2 → RapidOCR
```

Two complementary error measures are recorded:

- Mean line error — sensitive to the complete transcription, including punctuation and layout characters.
- Mean content error — normalizes punctuation and spacing to focus more directly on textual recognition.

Benchmark results are written automatically to:
```text
benchmarks/results/ocr_benchmark_latest.csv
```

### Initial Experimental Result
---
On the first manually verified historical-document crop, mean content error was:

```text
RapidOCR 2×              0.143
RapidOCR 3×              0.110
RealESRGAN x2 + RapidOCR 0.091
```
The learned enhancement therefore improved recognition on this sample, but at substantially greater computational cost on a CPU-only system.

These results are experimental and sample-specific. Additional ground-truth samples are being added before broader conclusions are drawn.


### AI Enhancement
---
The current learned enhancement experiment uses:

- PyTorch
- torchvision
- Spandrel
- RealESRGAN_x2plus pretrained weights

Model weights are deliberately excluded from Git.

AI enhancement is treated as an experimental preprocessing stage rather than as ground truth. Recognition quality is evaluated against human-verified source transcription.

### Installation
---
Create and activate a Python virtual environment, then install the recorded environment:

```bash
python -m pip install -r requirements.txt
```
The current development environment uses Python 3.14.

## Basic Usage

Convert a directory recursively:

```bash
python scripts/pdf_to_text.py \
  --input path/to/pdfs \
  --output path/to/text_output
```

Run the OCR scale benchmark:

```bash
python benchmarks/compare_ocr.py
```

Run the multi-crop content-aware benchmark:

```bash
python benchmarks/compare_crop_ocr.py
```
Run the AI enhancement experiment:

```bash
python benchmarks/compare_ai_enhancement.py
```
Check a Python script:

```bash
python scripts/check_python.py path/to/script.py
```

## Reproducibility

The repository records:

- exact Python package versions in requirements.txt
- manually verified ground-truth samples
- benchmark methodology
- generated benchmark results
- processing times
- tagged development milestones

Large pretrained model weights and private document collections remain local.

## Provenance
---
This project originated from:

frankcasas/PDF-to-Text

The original repository is retained locally as the Git remote upstream.

Development of pdf_text_toolkit adds OCR fallback, experimental learned image enhancement, benchmarking, ground-truth evaluation, reproducibility tooling and an expanded project structure.

## Status

Current milestone: v0.4.0

The project is under active development.
