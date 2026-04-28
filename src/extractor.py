"""
extractor.py — Key-field extraction from OCR text lines.

Extracts:
  • store_name
  • date
  • items  (name + price pairs)
  • total_amount

Each field is returned as:
  { "value": ..., "confidence": float, "flagged": bool (optional) }
"""
import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Regex patterns ─────────────────────────────────────────────────────────────

DATE_PATTERNS = [
    r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b",
    r"\b(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b",
    r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{2,4})\b",
    r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
]

TOTAL_KEYWORDS = [
    r"\bTOTAL\b",
    r"\bGRAND\s+TOTAL\b",
    r"\bAMOUNT\s+DUE\b",
    r"\bBALANCE\s+DUE\b",
    r"\bNET\s+TOTAL\b",
    r"\bFINAL\s+TOTAL\b",
    r"\bTOTAL\s+AMOUNT\b",
    r"\bAMT\s+DUE\b",
]

PRICE_RE = re.compile(
    r"(?:Rs\.?|INR|\u20b9|\$|\u20ac|\u00a3)?\s*(\d{1,6}(?:[,\.]\d{2,3})*(?:\.\d{2})?)"
)

STORE_NOISE = {
    "receipt", "invoice", "bill", "tax", "gst", "vat", "thank", "you",
    "visit", "again", "cashier", "customer", "copy", "tel", "phone",
    "www", "http",
}

SKIP_ITEM_RE = re.compile(
    r"\b(total|subtotal|sub-total|tax|gst|vat|service|discount|change|"
    r"cash|card|tip|balance|due)\b",
    re.IGNORECASE,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _combine_confidence(ocr_conf: float, text_conf: float, ocr_weight: float = 0.3) -> float:
    """Weighted blend of OCR-level and heuristic text confidence."""
    combined = ocr_weight * ocr_conf + (1 - ocr_weight) * text_conf
    return round(min(max(combined, 0.0), 1.0), 3)


def _clean_price(raw: str) -> Optional[str]:
    """Normalise a raw price string to a plain decimal string."""
    if not raw:
        return None
    raw = re.sub(r"[^\d.,]", "", raw).strip()
    if not raw:
        return None
    # Thousands-comma format: 1,234.56 → 1234.56
    if re.match(r"^\d{1,3}(,\d{3})+(\.\d{2})?$", raw):
        raw = raw.replace(",", "")
    return raw


def _flag(result: dict, threshold: float) -> dict:
    """Add 'flagged' key if confidence is below threshold."""
    if result.get("confidence", 1.0) < threshold:
        result["flagged"] = True
    return result


# ── Public extraction functions ────────────────────────────────────────────────

def extract_store_name(lines: List[str], ocr_conf: float, cfg: dict) -> dict:
    """
    Heuristically identify the store/vendor name from the top lines of the receipt.
    """
    max_lines = cfg["extraction"].get("max_store_name_lines", 8)
    max_len = cfg["extraction"].get("max_store_name_len", 60)
    threshold = cfg["extraction"].get("low_confidence_threshold", 0.7)
    ocr_weight = cfg["confidence"].get("ocr_weight", 0.3)

    candidates: List[Tuple[str, float]] = []

    for i, line in enumerate(lines[:max_lines]):
        if len(line) < 3 or len(line) > max_len:
            continue
        if re.search(r"\d{5,}", line):          # long digit runs → not a name
            continue
        words = line.lower().split()
        if any(w in STORE_NOISE for w in words):
            continue
        if PRICE_RE.search(line) and any(c.isdigit() for c in line[:5]):
            continue

        score = 1.0 - i * 0.08
        if line.isupper():
            score += 0.15
        if line.istitle():
            score += 0.10
        digit_ratio = sum(c.isdigit() for c in line) / max(len(line), 1)
        score -= digit_ratio * 0.5
        score = min(max(score, 0.1), 1.0)
        candidates.append((line, score))

    if not candidates:
        return _flag({"value": None, "confidence": 0.0}, threshold)

    best, text_conf = sorted(candidates, key=lambda x: -x[1])[0]
    conf = _combine_confidence(ocr_conf, text_conf, ocr_weight=ocr_weight + 0.1)
    return _flag({"value": best, "confidence": conf}, threshold)


def extract_date(lines: List[str], ocr_conf: float, cfg: dict) -> dict:
    """Find the first date-like string in the OCR lines."""
    threshold = cfg["extraction"].get("low_confidence_threshold", 0.7)
    ocr_weight = cfg["confidence"].get("ocr_weight", 0.3)

    for line in lines:
        for pat in DATE_PATTERNS:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                labelled = bool(re.search(r"\b(date|dated|dt)\b", line, re.IGNORECASE))
                text_conf = 0.95 if labelled else 0.80
                conf = _combine_confidence(ocr_conf, text_conf, ocr_weight)
                return _flag({"value": m.group(1), "confidence": conf}, threshold)

    return _flag({"value": None, "confidence": 0.0}, threshold)


def extract_total(lines: List[str], ocr_conf: float, cfg: dict) -> dict:
    """
    Find the grand total amount.
    Primary: lines containing a TOTAL keyword.
    Fallback: largest numeric value on the receipt.
    """
    threshold = cfg["extraction"].get("low_confidence_threshold", 0.7)
    ocr_weight = cfg["confidence"].get("ocr_weight", 0.3)

    candidates: List[Tuple[str, float]] = []

    for line in lines:
        if any(re.search(kw, line.upper()) for kw in TOTAL_KEYWORDS):
            m = PRICE_RE.search(line)
            if m:
                amount = _clean_price(m.group(1))
                if amount:
                    conf = _combine_confidence(ocr_conf, 0.95, ocr_weight)
                    candidates.append((amount, conf))

    if candidates:
        amount, conf = candidates[-1]   # last match = grand total
        return _flag({"value": amount, "confidence": conf}, threshold)

    # Fallback: largest number on the receipt
    all_prices: List[Tuple[float, str]] = []
    for line in lines:
        for m in PRICE_RE.finditer(line):
            val = _clean_price(m.group(1))
            if val:
                try:
                    all_prices.append((float(val.replace(",", "")), val))
                except ValueError:
                    pass

    if all_prices:
        _, raw_val = max(all_prices, key=lambda x: x[0])
        conf = _combine_confidence(ocr_conf, 0.45, ocr_weight)
        return _flag({"value": raw_val, "confidence": conf}, threshold)

    return _flag({"value": None, "confidence": 0.0}, threshold)


def extract_items(lines: List[str], ocr_conf: float, cfg: dict) -> List[dict]:
    """
    Extract line-item pairs (name, price) from the receipt body.

    Strategy: look for lines that contain a price but are NOT total/tax lines.
    The item name is taken from the same line (left of the price) or the
    preceding line if the current line is price-only.
    """
    threshold = cfg["extraction"].get("low_confidence_threshold", 0.7)
    ocr_weight = cfg["confidence"].get("ocr_weight", 0.3)

    items: List[dict] = []
    prev_line = ""

    for line in lines:
        if SKIP_ITEM_RE.search(line):
            prev_line = line
            continue

        m = PRICE_RE.search(line)
        if not m:
            prev_line = line
            continue

        price_raw = _clean_price(m.group(1))
        if not price_raw:
            prev_line = line
            continue

        # Derive item name
        name_part = line[: m.start()].strip(" :-")
        if len(name_part) < 2:
            name_part = prev_line.strip()

        if len(name_part) < 2:
            prev_line = line
            continue

        # Skip if name looks like a total/tax label
        if SKIP_ITEM_RE.search(name_part):
            prev_line = line
            continue

        conf = _combine_confidence(ocr_conf, 0.75, ocr_weight)
        item: dict = {
            "name": name_part,
            "price": price_raw,
            "confidence": conf,
        }
        if conf < threshold:
            item["flagged"] = True
        items.append(item)
        prev_line = line

    return items


def extract_all(
    ocr_results: List[Tuple[str, float]],
    ocr_conf: float,
    cfg: dict,
) -> dict:
    """
    Run all extractors and return a combined structured dict.

    Parameters
    ----------
    ocr_results : list of (text, confidence) tuples
    ocr_conf    : mean OCR confidence for the image
    cfg         : full pipeline config dict

    Returns
    -------
    dict with keys: store_name, date, items, total_amount, flags
    """
    lines = [text for text, _ in ocr_results]
    flags: List[str] = []

    store = extract_store_name(lines, ocr_conf, cfg)
    date = extract_date(lines, ocr_conf, cfg)
    total = extract_total(lines, ocr_conf, cfg)
    items = extract_items(lines, ocr_conf, cfg)

    # Collect flags
    for field_name, field in [("store_name", store), ("date", date), ("total_amount", total)]:
        if field.get("flagged"):
            flags.append(f"LOW_CONFIDENCE:{field_name}({field['confidence']})")

    if not items:
        flags.append("NO_ITEMS_DETECTED")

    return {
        "store_name": store,
        "date": date,
        "items": items,
        "total_amount": total,
        "flags": flags,
    }
