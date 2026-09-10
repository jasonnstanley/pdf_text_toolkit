# OCR Benchmark

Purpose: compare deterministic OCR against AI-assisted enhancement/OCR on historical scanned electoral-roll pages.

Baseline candidates:
- RapidOCR at 2x render
- RapidOCR at 3x render
- OpenCV preprocessing + RapidOCR

Planned AI benchmark:
- PyTorch-based image enhancement or OCR model
- Compare against manually transcribed ground truth

Metrics:
- Character error rate
- Word error rate
- Name accuracy
- Address/number accuracy
- Processing time
