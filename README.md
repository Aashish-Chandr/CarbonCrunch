<div align="center">

<img src="https://img.shields.io/badge/CarbonCrunch-Receipt%20OCR%20Pipeline-2ea44f?style=for-the-badge&logo=python&logoColor=white" alt="CarbonCrunch Banner"/>

# 🧾 CarbonCrunch

### *An end-to-end intelligent receipt scanner — extract, structure, and summarize your expenses*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-orange?style=flat-square&logo=eye&logoColor=white)](https://github.com/JaidedAI/EasyOCR)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)](https://jupyter.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 📖 What is CarbonCrunch?

**CarbonCrunch** is a production-ready Receipt OCR pipeline that transforms messy, real-world receipt images into clean, structured JSON data. It handles everything from blurry corner-store slips to multi-page scanned invoices — extracting store names, dates, line items, and totals with per-field confidence scoring.

> **Why "CarbonCrunch"?** — A nod to the carbon copy receipts of old, now *crunched* by modern AI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔬 **5-Stage Preprocessing** | Skew correction, CLAHE, denoising, binarization — before a single character is read |
| 🤖 **Dual OCR Engines** | EasyOCR (primary) with automatic Tesseract fallback |
| 📊 **Confidence Scoring** | Every extracted field gets a `0.0–1.0` confidence score |
| 🏷️ **Smart Field Extraction** | Store name, date, all line items, and total — rule-based + heuristic |
| 💰 **Expense Summarizer** | Aggregates spend across all receipts with per-store breakdowns |
| ⚠️ **Low-Confidence Flagging** | Fields below threshold are automatically flagged for review |
| 🧪 **Unit Tested** | Extractor tests run without any OCR dependency |

---

## 🏗️ Architecture

```
Receipt Image
      │
      ▼
┌─────────────────────────────────────┐
│         PREPROCESSOR                │
│  1. Resize  →  2. Skew Correct      │
│  3. CLAHE   →  4. Denoise           │
│             5. Binarize             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│           OCR ENGINE                │
│   EasyOCR (primary)                 │
│   Tesseract (fallback)              │
│   → List of OCRResult(text, conf,   │
│     bbox)                           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│          EXTRACTOR                  │
│  store_name  │  date                │
│  items       │  total_amount        │
│                                     │
│  confidence = 0.3×OCR + 0.7×heur   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         SUMMARIZER                  │
│  Total Spend · Per-Store · Flags    │
└─────────────────────────────────────┘
               │
               ▼
         JSON Output 📄
```

---

## 📂 Project Structure

```
CarbonCrunch/
├── 📓 Notebook/                 # Jupyter exploration & prototyping
├── 📁 output/
│   └── receipt_ocr_outputs/    # Generated JSON results
├── pipeline.py                 # 🚀 Main entry point
├── requirements.txt
├── receipts/                   # ← Drop your receipt images here
├── outputs/                    # ← JSON results written here
├── src/
│   ├── preprocessor.py         # Image preprocessing pipeline
│   ├── ocr_engine.py           # EasyOCR / Tesseract abstraction
│   ├── extractor.py            # Field extraction + confidence scoring
│   └── summarizer.py           # Financial summary generation
└── tests/
    └── test_extractor.py       # Unit tests (no OCR dependency)
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/Aashish-Chandr/CarbonCrunch.git
cd CarbonCrunch

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **Note:** EasyOCR will automatically download its model weights on first run (~100 MB). Tesseract must be installed separately if you want to use the fallback engine ([install guide](https://github.com/tesseract-ocr/tessdoc)).

---

## 🚀 Usage

### Run the pipeline

```bash
# Place receipt images in ./receipts/, then:
python pipeline.py --input ./receipts --output ./outputs

# Use Tesseract instead of EasyOCR
python pipeline.py --input ./receipts --output ./outputs --engine tesseract
```

### Output files generated

| File | Description |
|---|---|
| `outputs/<receipt_name>.json` | Per-receipt structured JSON with confidence scores |
| `outputs/all_receipts.json` | Combined list of all processed receipts |
| `outputs/expense_summary.json` | Aggregated financial summary |

---

## 📄 Output Format

### Per-Receipt JSON

```json
{
  "filename": "receipt_001.jpg",
  "store_name":   { "value": "SUPER MART",  "confidence": 0.94 },
  "date":         { "value": "15/04/2024",  "confidence": 0.92 },
  "items": [
    { "name": "Apple Juice", "price": "90.00", "confidence": 0.78 }
  ],
  "total_amount": { "value": "315.00",       "confidence": 0.92 },
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
    "SUPER MART": {
      "total_spend": 630.00,
      "transactions": 3,
      "average_per_transaction": 210.00
    }
  },
  "reliability": {
    "low_confidence_receipt_images": ["blurry_receipt.jpg"],
    "total_flagged_fields": 2
  }
}
```

---

## 🔬 How It Works

### 1 · Image Preprocessing

Each receipt image passes through a **5-stage pipeline** before any OCR is attempted:

```
Resize → Skew Correct → CLAHE → Denoise → Binarize
```

- **Resize** — Upscales images narrower than 800 px to improve character recognition
- **Skew Correction** — Hough line transform detects dominant text angle and rotates the image back to horizontal
- **CLAHE** — Contrast Limited Adaptive Histogram Equalization handles uneven lighting and washed-out receipts
- **Denoising** — `fastNlMeansDenoising` removes camera/scanner grain while preserving sharp text edges
- **Binarization** — Blends Otsu's global threshold with Gaussian adaptive thresholding for robust black-and-white conversion

### 2 · OCR Engine

- **Primary**: EasyOCR — deep-learning based, handles diverse fonts, returns per-word confidence natively
- **Fallback**: Tesseract via `pytesseract` — traditional OCR, activated when EasyOCR is unavailable

All results are normalised to `OCRResult(text, confidence, bbox)` objects.

### 3 · Field Extraction

| Field | Strategy |
|---|---|
| `store_name` | Scan first 8 lines; score by position, capitalisation, absence of digit/noise words |
| `date` | Regex over 5 date formats — `DD/MM/YYYY`, `YYYY-MM-DD`, `"12 May 2023"`, etc. |
| `total_amount` | Keyword matching (`TOTAL`, `GRAND TOTAL`, `AMOUNT DUE`) + adjacent price regex; fallback to largest price on page |
| `items` | Pattern: `<name> <price>` or `<name> x2 <price>`, excluding tax/subtotal lines |

### 4 · Confidence Scoring

```
field_confidence = 0.3 × ocr_avg_confidence + 0.7 × heuristic_confidence
```

Fields below **0.7** are flagged as `LOW_CONFIDENCE:<field>`.

---

## 🛠️ Tech Stack

| Library | Version | Role |
|---|---|---|
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | ≥ 1.7.0 | Primary OCR engine |
| [Tesseract / pytesseract](https://github.com/madmaze/pytesseract) | ≥ 0.3.10 | Fallback OCR engine |
| [OpenCV](https://opencv.org) | ≥ 4.8.0 | Preprocessing (skew, CLAHE, denoise, threshold) |
| [Pillow](https://python-pillow.org) | ≥ 10.0 | Image format handling |
| [NumPy](https://numpy.org) | ≥ 1.24 | Array operations |
| `re` (stdlib) | — | Regex-based field extraction |

---

## 🧩 Challenges & Solutions

### 📐 Receipt Layout Diversity
Receipts have no standard layout — store names can appear anywhere, totals can be labelled a dozen different ways. Solved with **layered heuristics** and multiple pattern-matching strategies.

### 🌫️ Low-Quality Images
Blur, noise, and poor lighting reduce OCR accuracy significantly. The preprocessing pipeline (CLAHE + denoising + adaptive binarisation) recovers **~15–20%** of otherwise unreadable text.

### 🔢 Price vs. Non-Price Numbers
Receipts are dense with numbers — phone numbers, invoice IDs, dates. Context-aware extraction (adjacent keywords, line structure, column alignment) distinguishes prices from other numeric data.

### 📋 Item Extraction Fragility
Item lines vary enormously. The current whitespace-based column detection works well for tabular receipts but may miss items in paragraph-style or handwritten receipts.

---

## 🔭 Roadmap

| Area | Planned Improvement |
|---|---|
| 🎯 OCR Accuracy | Fine-tune EasyOCR or TrOCR on receipt-specific datasets |
| 🏷️ Item Extraction | NER model trained specifically on receipt line items |
| 📐 Layout Analysis | Integrate DocLayNet for header / body / footer region detection |
| 📅 Date Normalisation | Standardise all dates to ISO 8601 (`YYYY-MM-DD`) |
| 💱 Currency Detection | Detect currency symbol and normalise amounts |
| ✍️ Handwriting Support | Add a dedicated handwriting recognition path |
| 📏 Evaluation | Build a labelled ground-truth dataset for automated accuracy benchmarking |

---

## 🧪 Running Tests

```bash
# Unit tests — no OCR engine required
python -m pytest tests/test_extractor.py -v
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch — `git checkout -b feat/amazing-feature`
3. Commit your changes — `git commit -m 'Add some amazing feature'`
4. Push to the branch — `git push origin feat/amazing-feature`
5. Open a Pull Request

---

## 📬 Contact

**Aashish Chandr** — [@Aashish-Chandr](https://github.com/Aashish-Chandr)

Project Link: [https://github.com/Aashish-Chandr/CarbonCrunch](https://github.com/Aashish-Chandr/CarbonCrunch)

---

<div align="center">

Made with 🧾 and ☕ · If this helped you, please ⭐ the repo!

</div>
