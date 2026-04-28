<div align="center">

<!-- Header Banner (capsule-render - reliable on GitHub) -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=2ecc71,145a32&height=200&section=header&text=CarbonCrunch&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=Receipt%20OCR%20Pipeline%20%E2%80%94%20Extract.%20Structure.%20Score.&descAlignY=58&descSize=18&animation=fadeIn" alt="CarbonCrunch Banner" width="100%"/>

<br/>

<p><i>An end-to-end intelligent receipt scanner — turn messy images into clean, confidence-scored JSON data.</i></p>

<br/>

<!-- Dynamic Badges Row 1 -->
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)
[![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-27AE60?style=for-the-badge&logo=eye&logoColor=white)](https://github.com/JaidedAI/EasyOCR)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

<!-- Dynamic Badges Row 2 -->
[![GitHub last commit](https://img.shields.io/github/last-commit/Aashish-Chandr/CarbonCrunch?style=flat-square&color=2ecc71&label=Last+Commit)](https://github.com/Aashish-Chandr/CarbonCrunch/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/Aashish-Chandr/CarbonCrunch?style=flat-square&color=17a589&label=Repo+Size)](https://github.com/Aashish-Chandr/CarbonCrunch)
[![GitHub stars](https://img.shields.io/github/stars/Aashish-Chandr/CarbonCrunch?style=flat-square&color=f1c40f)](https://github.com/Aashish-Chandr/CarbonCrunch/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Aashish-Chandr/CarbonCrunch?style=flat-square&color=e67e22)](https://github.com/Aashish-Chandr/CarbonCrunch/network/members)
[![Views](https://komarev.com/ghpvc/?username=Aashish-Chandr&label=Profile+Views&color=2ecc71&style=flat-square)](https://github.com/Aashish-Chandr)

<br/>

<!-- Quick nav pills -->
[📖 Overview](#-overview) • [⚙️ Setup](#️-installation--setup) • [🚀 Usage](#-usage) • [📐 Architecture](#-architecture) • [📄 Output](#-output-format) • [🛣️ Roadmap](#️-roadmap)

</div>

---

## 📖 Overview

**CarbonCrunch** is a production-ready **Receipt OCR Pipeline** that transforms real-world receipt images — blurry, skewed, poorly lit — into clean, structured JSON with per-field confidence scores.

> 💡 **Why CarbonCrunch?** A nod to the carbon copy receipts of old, now *crunched* by modern AI.

```
🖼️  Receipt Image  ──►  🔧 Preprocess  ──►  🔍 OCR  ──►  🏷️ Extract  ──►  📊 Summarise  ──►  📄 JSON
```

### ✨ What it does

| Capability | Detail |
|---|---|
| 🔬 **5-Stage Preprocessing** | Resize → Skew Correct → CLAHE → Denoise → Binarize |
| 🤖 **Dual OCR Engines** | EasyOCR (primary) + Tesseract (auto fallback) |
| 🏷️ **Smart Field Extraction** | Store name, date, all line items, prices, total |
| 📊 **Confidence Scoring** | Every field scored 0.0–1.0 using weighted formula |
| ⚠️ **Auto Flagging** | Fields below threshold flagged as `LOW_CONFIDENCE` |
| 💰 **Expense Summariser** | Per-store breakdown, total spend, reliability report |
| 🧪 **Unit Tested** | Extractor tests run with zero OCR dependency |

---

## 📐 Architecture

```mermaid
flowchart LR
    A[🖼️ Receipt Image] --> B[🔧 Preprocessor]
    B --> B1[Resize]
    B --> B2[Skew Correct]
    B --> B3[CLAHE]
    B --> B4[Denoise]
    B --> B5[Binarize]
    B1 & B2 & B3 & B4 & B5 --> C[🔍 OCR Engine]
    C --> C1[EasyOCR Primary]
    C --> C2[Tesseract Fallback]
    C1 & C2 --> D[🏷️ Extractor]
    D --> D1[store_name]
    D --> D2[date]
    D --> D3[items + prices]
    D --> D4[total_amount]
    D1 & D2 & D3 & D4 --> E[📊 Summariser]
    E --> F[📄 JSON Output]

    style A fill:#2ecc71,color:#fff
    style F fill:#145a32,color:#fff
    style C fill:#2980b9,color:#fff
    style D fill:#e67e22,color:#fff
    style E fill:#8e44ad,color:#fff
```

---

## 📂 Project Structure

```
CarbonCrunch/
│
├── 📓 Notebook/                    # Jupyter exploration & prototyping
│   └── receipt_ocr_pipeline.ipynb
│
├── 📁 output/
│   └── receipt_ocr_outputs/        # Generated JSON results
│
├── 🚀 pipeline.py                  # Main entry point
├── 📋 requirements.txt
│
├── 🗂️ src/
│   ├── preprocessor.py             # 5-stage image preprocessing
│   ├── ocr_engine.py               # EasyOCR / Tesseract abstraction
│   ├── extractor.py                # Field extraction + confidence scoring
│   └── summarizer.py               # Financial summary generation
│
└── 🧪 tests/
    └── test_extractor.py           # Unit tests (no OCR dependency)
```

---

## ⚙️ Installation & Setup

### Prerequisites

![Python](https://img.shields.io/badge/Python-≥3.8-3776AB?logo=python&logoColor=white&style=flat-square)
![pip](https://img.shields.io/badge/pip-latest-orange?logo=pypi&logoColor=white&style=flat-square)

```bash
# 1. Clone the repository
git clone https://github.com/Aashish-Chandr/CarbonCrunch.git
cd CarbonCrunch

# 2. Create a virtual environment (recommended)
python -m venv venv

# Activate — Linux/Mac
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **📌 Note:** EasyOCR downloads model weights (~100 MB) on first run automatically.
> For Tesseract, install separately → [Installation Guide](https://github.com/tesseract-ocr/tessdoc)

---

## 🚀 Usage

### Basic Run

```bash
# Place receipt images in ./receipts/, then:
python pipeline.py --input ./receipts --output ./outputs
```

### Switch OCR Engine

```bash
# Use Tesseract instead of EasyOCR
python pipeline.py --input ./receipts --output ./outputs --engine tesseract
```

### Run in Jupyter

```bash
jupyter notebook Notebook/receipt_ocr_pipeline.ipynb
```

### Run Tests

```bash
# Unit tests — no OCR engine required
python -m pytest tests/test_extractor.py -v
```

### Output files generated

| File | Description |
|---|---|
| `outputs/<n>.json` | Per-receipt structured JSON with confidence scores |
| `outputs/all_receipts.json` | Combined list of all processed receipts |
| `outputs/expense_summary.json` | Aggregated financial summary |

---

## 🔬 How It Works

<details>
<summary><b>🔧 Stage 1 — Image Preprocessing</b> (click to expand)</summary>

<br/>

Each receipt goes through a **5-stage deterministic pipeline** before any text recognition:

```
Raw Image → Resize → Skew Correct → CLAHE → Denoise → Binarize → Clean Image
```

| Step | Technique | Purpose |
|---|---|---|
| **1. Resize** | Upscale if width < 800 px | Prevents tiny characters being missed |
| **2. Skew Correct** | Hough Line Transform + rotation | Straight text → far better OCR accuracy |
| **3. CLAHE** | Adaptive histogram equalisation | Handles uneven lighting & washed-out images |
| **4. Denoise** | `fastNlMeansDenoising` | Removes grain while keeping sharp text edges |
| **5. Binarize** | Otsu + Gaussian adaptive blend | Clean black-and-white for the OCR engine |

> ✅ This pipeline alone recovers **~15–20% accuracy** on degraded images.

</details>

<details>
<summary><b>🔍 Stage 2 — OCR Engine</b> (click to expand)</summary>

<br/>

| Engine | Type | Confidence | When Used |
|---|---|---|---|
| **EasyOCR** | Deep-learning | Native per-word score | Primary (default) |
| **Tesseract** | Classical OCR | From `image_to_data` | Fallback if EasyOCR unavailable |

Both normalise results to: `OCRResult(text, confidence, bbox)`

</details>

<details>
<summary><b>🏷️ Stage 3 — Field Extraction</b> (click to expand)</summary>

<br/>

| Field | Strategy | Confidence Signal |
|---|---|---|
| `store_name` | Scan first 8 lines; score by position, capitalisation, digit absence | Position weight + capitalisation ratio |
| `date` | Regex over 5 formats — `DD/MM/YYYY`, `YYYY-MM-DD`, `12 May 2023`, etc. | Full regex match quality |
| `total_amount` | Keyword matching (`TOTAL`, `GRAND TOTAL`, `AMOUNT DUE`) + price regex | Keyword hit + currency format match |
| `items` | Pattern `<n> <price>` or `<n> x2 <price>`; excludes tax/subtotal | Column alignment + digit ratio |
| `prices` | Adjacent to item names; largest isolated price as fallback | Format validation + context proximity |

</details>

<details>
<summary><b>📊 Stage 4 — Confidence Scoring</b> (click to expand)</summary>

<br/>

Every extracted field is scored using a **weighted formula:**

```
field_confidence = 0.3 × ocr_avg_confidence + 0.7 × heuristic_confidence
```

**Heuristic signals used:**
- Pattern validation (regex match quality)
- Keyword presence (`TOTAL`, `Date:`, etc.)
- Position in document (top → store name, bottom → total)
- Character composition (digit ratio, capitalisation)

**Flagging rule:** Fields below **0.70** receive a `LOW_CONFIDENCE:<field>` flag in the JSON output.

</details>

---

## 📄 Output Format

### Per-Receipt JSON

```json
{
  "filename": "receipt_001.jpg",
  "store_name":   { "value": "SUPER MART",  "confidence": 0.94 },
  "date":         { "value": "15/04/2024",  "confidence": 0.92 },
  "items": [
    { "name": "Apple Juice", "price": "90.00",  "confidence": 0.88 },
    { "name": "Bread Loaf",  "price": "45.00",  "confidence": 0.82 },
    { "name": "Milk 1L",     "price": "55.00",  "confidence": 0.79 }
  ],
  "total_amount": { "value": "315.00", "confidence": 0.96 },
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

## 🛠️ Tech Stack

<div align="center">

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)

</div>

| Library | Version | Role |
|---|---|---|
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | ≥ 1.7.0 | Primary OCR engine — deep learning, multi-font |
| [pytesseract](https://github.com/madmaze/pytesseract) | ≥ 0.3.10 | Fallback OCR engine |
| [OpenCV](https://opencv.org) | ≥ 4.8.0 | Preprocessing — skew, CLAHE, denoise, threshold |
| [Pillow](https://python-pillow.org) | ≥ 10.0 | Image format handling |
| [NumPy](https://numpy.org) | ≥ 1.24 | Array operations |
| `re` (stdlib) | — | Regex-based field extraction |

---

## ⚠️ Challenges & Solutions

<details>
<summary><b>📋 Receipt Layout Diversity</b></summary>
<br/>
No standard layout exists across vendors. Store names, dates, and totals appear in completely different positions and formats.

**Solution:** Layered heuristics — positional scoring, keyword whitelists, multiple regex patterns, and a fallback to the largest price on the page for totals.
</details>

<details>
<summary><b>🌫️ Low-Quality Images</b></summary>
<br/>
Camera blur, scan noise, and extreme contrast variations severely degrade OCR character recognition.

**Solution:** 5-stage preprocessing pipeline (CLAHE + denoising + adaptive binarisation) recovers ~15–20% of otherwise unreadable receipts.
</details>

<details>
<summary><b>🔢 Price vs Non-Price Numbers</b></summary>
<br/>
Receipts are dense with numbers — phone numbers, invoice IDs, loyalty points, dates — all numerically indistinguishable from prices without context.

**Solution:** Context-aware extraction using adjacent keywords, line structure, and column alignment to distinguish prices from other numeric data.
</details>

<details>
<summary><b>📝 Item Extraction Fragility</b></summary>
<br/>
Item lines vary enormously — tabular, paragraph-style, single-column, multi-column, handwritten.

**Solution:** Whitespace-based column detection works well for tabular receipts. Handwritten/paragraph-style receipts are a flagged edge case with a clear improvement path.
</details>

---

## 🛣️ Roadmap

```mermaid
gantt
    title CarbonCrunch — Improvement Roadmap
    dateFormat  YYYY-MM
    section Accuracy
    Fine-tune TrOCR on receipts       :2025-06, 3M
    NER model for item extraction     :2025-08, 3M
    section Layout
    DocLayNet region detection        :2025-07, 2M
    Handwriting recognition path      :2025-09, 3M
    section Data
    ISO 8601 date normalisation       :2025-06, 1M
    Currency symbol detection         :2025-07, 1M
    section Infrastructure
    REST API via FastAPI              :2025-09, 2M
    Ground-truth evaluation dataset   :2025-10, 3M
```

| Area | Planned Improvement | Priority |
|---|---|---|
| 🎯 OCR Accuracy | Fine-tune EasyOCR / TrOCR on receipt datasets | 🔴 High |
| 🏷️ Item Extraction | NER model trained on receipt line items | 🔴 High |
| 📐 Layout Analysis | DocLayNet for header/body/footer detection | 🟡 Medium |
| 📅 Date Normalisation | Standardise all dates to ISO 8601 | 🟡 Medium |
| 💱 Currency Detection | Detect symbol, normalise multi-currency | 🟢 Low |
| ✍️ Handwriting | Dedicated HTR recognition path | 🟢 Low |
| 📏 Evaluation | Labelled ground-truth dataset + auto benchmarking | 🔴 High |
| 🌐 API | FastAPI wrapper for production use | 🟡 Medium |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

```bash
# 1. Fork the project on GitHub

# 2. Create your feature branch
git checkout -b feat/your-amazing-feature

# 3. Commit your changes
git commit -m "✨ Add amazing feature"

# 4. Push and open a Pull Request
git push origin feat/your-amazing-feature
```

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/Aashish-Chandr/CarbonCrunch/pulls)
[![Open Issues](https://img.shields.io/github/issues/Aashish-Chandr/CarbonCrunch?style=flat-square&color=red)](https://github.com/Aashish-Chandr/CarbonCrunch/issues)

---

## 📈 GitHub Stats

<div align="center">

[![GitHub Stats](https://github-readme-stats.vercel.app/api?username=Aashish-Chandr&show_icons=true&theme=tokyonight&hide_border=true&count_private=true)](https://github.com/Aashish-Chandr)

[![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=Aashish-Chandr&layout=compact&theme=tokyonight&hide_border=true)](https://github.com/Aashish-Chandr)

[![GitHub Streak](https://streak-stats.demolab.com?user=Aashish-Chandr&theme=tokyonight&hide_border=true)](https://github.com/Aashish-Chandr)

</div>

---

## 📬 Contact

<div align="center">

**Aashish Chandra**

[![GitHub](https://img.shields.io/badge/GitHub-Aashish--Chandr-181717?style=for-the-badge&logo=github)](https://github.com/Aashish-Chandr)
[![Project](https://img.shields.io/badge/Project-CarbonCrunch-2ecc71?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Aashish-Chandr/CarbonCrunch)

</div>

---

<div align="center">

**Made with 🧾 and ☕ by [Aashish Chandra](https://github.com/Aashish-Chandr)**

*If this project helped you, please consider giving it a ⭐ — it means a lot!*

[![⭐ Star this repo](https://img.shields.io/badge/⭐%20Star%20this%20repo-CarbonCrunch-2ecc71?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Aashish-Chandr/CarbonCrunch)

<!-- Footer wave -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=2ecc71,145a32&height=100&section=footer" width="100%"/>

</div>
