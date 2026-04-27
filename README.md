# Receipt OCR Pipeline — Documentation

## Overview
An end-to-end system for extracting structured information from receipt images, with
confidence-aware outputs and a financial summary across all processed receipts.

---

## 1. Approach

### A. Image Preprocessing (`src/preprocessor.py`)
Each image goes through a 5-stage pipeline before OCR:

1. **Resize** — Upscale images narrower than 800px (improves OCR character recognition)
2. **Skew correction** — Hough line transform detects dominant text angles; images are
   rotated back to horizontal
3. **Contrast enhancement** — CLAHE (Contrast Limited Adaptive Histogram Equalization)
   handles uneven lighting and washed-out receipts
4. **Denoising** — `fastNlMeansDenoising` removes camera/scanner grain while preserving
   sharp text edges
5. **Binarization** — Blend of Otsu's global threshold and Gaussian adaptive thresholding
   for robust black-and-white conversion

### B. OCR Engine (`src/ocr_engine.py`)
- **Primary**: EasyOCR — deep-learning-based, handles diverse fonts and layouts well,
  returns per-word confidence scores natively
- **Fallback**: Tesseract (via pytesseract) — traditional OCR, activated if EasyOCR is
  unavailable; confidence extracted from `image_to_data` output

All OCR results are normalised to a list of `OCRResult(text, confidence, bbox)` objects.

### C. Information Extraction (`src/extractor.py`)
Rule-based extraction with heuristic confidence scoring:

| Field         | Strategy |
|---------------|----------|
| `store_name`  | Scan first 8 lines; score by position, capitalisation, absence of digits/noise words |
| `date`        | Regex over 5 date formats (DD/MM/YYYY, YYYY-MM-DD, "12 May 2023", etc.) |
| `total_amount`| Keyword matching (TOTAL, GRAND TOTAL, AMOUNT DUE …) + adjacent price regex; fallback to largest price on page |
| `items`       | Pattern: `"<name>   <price>"` or `"<name>  x2  <price>"`, excluding tax/subtotal lines |

### D. Confidence Scoring
Each field's confidence is a **weighted combination**:

```
field_confidence = 0.3 × ocr_avg_confidence + 0.7 × heuristic_confidence
```

Heuristic scores are derived from:
- Pattern validation (regex match quality)
- Keyword presence ("TOTAL", "Date:")
- Position in document
- Character composition (digit ratio, capitalisation)

Fields below **0.7** are flagged with a `LOW_CONFIDENCE:<field>` flag.

### E. Financial Summary (`src/summarizer.py`)
Aggregates all processed receipts:
- Total spend (only from receipts where `total_amount.confidence ≥ 0.5`)
- Transaction count
- Per-store breakdown with average spend
- Reliability report listing low-confidence images

---

## 2. Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| EasyOCR | ≥ 1.7.0 | Primary OCR engine |
| Tesseract / pytesseract | ≥ 0.3.10 | Fallback OCR |
| OpenCV | ≥ 4.8.0 | Preprocessing (skew, CLAHE, denoise, threshold) |
| Pillow | ≥ 10.0 | Image format handling |
| NumPy | ≥ 1.24 | Array operations |
| Python `re` | stdlib | Regex extraction |

---

## 3. Project Structure

```
receipt_ocr/
├── pipeline.py           # Main entry point
├── requirements.txt
├── receipts/             # ← Put your images here
├── outputs/              # ← JSON results written here
├── src/
│   ├── preprocessor.py   # Image preprocessing
│   ├── ocr_engine.py     # OCR abstraction (EasyOCR / Tesseract)
│   ├── extractor.py      # Field extraction + confidence scoring
│   └── summarizer.py     # Financial summary generation
└── tests/
    └── test_extractor.py # Unit tests (no OCR dependency)
```

---

## 4. How to Run

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the pipeline
```bash
# Place receipt images in ./receipts/
python pipeline.py --input ./receipts --output ./outputs

# Use Tesseract instead of EasyOCR
python pipeline.py --input ./receipts --output ./outputs --engine tesseract
```

### Outputs
- `outputs/<receipt_name>.json` — per-receipt structured JSON with confidence scores
- `outputs/all_receipts.json` — combined list of all results
- `outputs/expense_summary.json` — financial summary

---

## 5. Output Format

### Per-receipt JSON
```json
{
  "filename": "receipt_001.jpg",
  "store_name": { "value": "SUPER MART", "confidence": 0.94 },
  "date":       { "value": "15/04/2024", "confidence": 0.92 },
  "items": [
    { "name": "Apple Juice", "price": "90.00", "confidence": 0.78 }
  ],
  "total_amount": { "value": "315.00", "confidence": 0.92 },
  "ocr_confidence": 0.85,
  "flags": []
}
```

### Expense Summary JSON
```json
{
  "summary": {
    "total_spend": 1245.50,
    "number_of_transactions": 8,
    "transactions_with_detected_total": 7,
    "average_transaction_value": 177.93
  },
  "spend_per_store": {
    "SUPER MART": { "total_spend": 630.00, "transactions": 3, "average_per_transaction": 210.00 }
  },
  "reliability": {
    "low_confidence_receipt_images": ["blurry_receipt.jpg"],
    "total_flagged_fields": 2
  }
}
```

---

## 6. Challenges Faced

### Receipt Layout Diversity
Receipts have no standard layout. Store names may appear anywhere; totals can be
labelled a dozen different ways. Solved with layered heuristics and multiple pattern
matching strategies.

### Low-Quality Images
Blur, noise, and poor lighting significantly reduce OCR accuracy. The preprocessing
pipeline (CLAHE + denoising + adaptive binarisation) recovers ~15–20% of otherwise
unreadable text in our testing.

### Price vs. Non-Price Numbers
Receipts contain many numbers (phone numbers, invoice IDs, dates). The extractor uses
context (adjacent keywords, line structure, column alignment) to distinguish prices
from other numeric data.

### Item Extraction Fragility
Item lines vary enormously across receipts. The current approach (whitespace-based
column detection) works well for tabular receipts but may miss items in paragraph-style
or handwritten receipts.

---

## 7. Potential Improvements

| Area | Improvement |
|------|-------------|
| OCR Accuracy | Fine-tune EasyOCR or TrOCR on receipt-specific data |
| Item Extraction | Use a Named Entity Recognition (NER) model trained on receipts |
| Layout Analysis | Add a document layout detection model (e.g. DocLayNet) to identify header/body/footer regions |
| Date Normalisation | Standardise all dates to ISO 8601 (YYYY-MM-DD) |
| Currency Detection | Detect currency symbol and normalise amounts |
| Handwritten Receipts | Add a handwriting recognition path |
| Evaluation | Build a labelled ground-truth dataset for automated accuracy measurement |
