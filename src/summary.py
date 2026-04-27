"""
summary.py — Financial summary generation from extracted receipt data.

Improvements over the original notebook:
  • Store name normalisation via fuzzy matching (rapidfuzz) to merge
    OCR variants of the same store (e.g. "RESTORAN WAN SHENG" vs
    "RESTORAN WAN  SHENG" vs "RESTTARAN HAN  SHENG").
  • Excludes receipts whose total_amount confidence is below threshold.
  • Returns a clean, well-typed summary dict.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from rapidfuzz import process as fuzz_process, fuzz
    _FUZZY_AVAILABLE = True
except ImportError:
    _FUZZY_AVAILABLE = False
    logger.warning("rapidfuzz not installed — store name normalisation disabled.")


def _normalise_store_name(name: str, canonical_names: List[str], threshold: int) -> str:
    """
    Return the best-matching canonical store name if similarity >= threshold,
    otherwise return the original name (which becomes a new canonical entry).
    """
    if not canonical_names or not _FUZZY_AVAILABLE:
        return name

    result = fuzz_process.extractOne(
        name, canonical_names,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold,
    )
    if result:
        return result[0]
    return name


def generate_summary(receipts: List[dict], cfg: dict) -> dict:
    """
    Build a financial summary from a list of per-receipt extraction dicts.

    Parameters
    ----------
    receipts : list
        Each element is the full output dict for one receipt (as saved to JSON).
    cfg : dict
        Full pipeline config dict.

    Returns
    -------
    dict with keys: summary, spend_per_store, reliability
    """
    min_conf = cfg["extraction"].get("low_confidence_threshold", 0.7)
    fuzzy_threshold = cfg["extraction"].get("store_name_fuzzy_threshold", 85)

    total_spend = 0.0
    n_transactions = len(receipts)
    n_with_total = 0
    low_conf_receipts: List[str] = []
    total_flagged_fields = 0

    # store_name → {"total_spend": float, "transactions": int}
    spend_per_store: Dict[str, Dict[str, Any]] = {}
    canonical_names: List[str] = []

    for receipt in receipts:
        filename = receipt.get("filename", "unknown")

        # ── Count flagged fields ──────────────────────────────────────────
        for field in ("store_name", "date", "total_amount"):
            if receipt.get(field, {}).get("flagged"):
                total_flagged_fields += 1

        # ── OCR-level reliability ─────────────────────────────────────────
        ocr_conf = receipt.get("ocr_confidence", 1.0)
        if ocr_conf < min_conf:
            low_conf_receipts.append(filename)

        # ── Total amount ──────────────────────────────────────────────────
        total_field = receipt.get("total_amount", {})
        total_conf = total_field.get("confidence", 0.0)
        total_val = total_field.get("value")

        amount = None
        if total_val is not None and total_conf >= min_conf * 0.7:
            try:
                amount = float(str(total_val).replace(",", ""))
            except (ValueError, TypeError):
                pass

        if amount is not None:
            total_spend += amount
            n_with_total += 1

        # ── Store spend ───────────────────────────────────────────────────
        store_field = receipt.get("store_name", {})
        store_raw = store_field.get("value")
        store_conf = store_field.get("confidence", 0.0)

        if store_raw and store_conf >= min_conf * 0.6:
            # Normalise to merge OCR variants
            store_key = _normalise_store_name(
                store_raw.strip(), canonical_names, fuzzy_threshold
            )
            if store_key not in canonical_names:
                canonical_names.append(store_key)

            entry = spend_per_store.setdefault(
                store_key, {"total_spend": 0.0, "transactions": 0}
            )
            entry["transactions"] += 1
            if amount is not None:
                entry["total_spend"] += amount

    # ── Compute averages ──────────────────────────────────────────────────
    for store_key, entry in spend_per_store.items():
        txns = entry["transactions"]
        entry["average_per_transaction"] = (
            round(entry["total_spend"] / txns, 2) if txns else 0.0
        )
        entry["total_spend"] = round(entry["total_spend"], 2)

    # Sort by total spend descending
    spend_per_store = dict(
        sorted(spend_per_store.items(), key=lambda x: -x[1]["total_spend"])
    )

    return {
        "summary": {
            "total_spend": round(total_spend, 2),
            "number_of_transactions": n_transactions,
            "transactions_with_detected_total": n_with_total,
            "average_transaction_value": (
                round(total_spend / n_with_total, 2) if n_with_total else 0.0
            ),
        },
        "spend_per_store": spend_per_store,
        "reliability": {
            "low_confidence_receipt_images": sorted(low_conf_receipts),
            "total_flagged_fields": total_flagged_fields,
            "note": "Transactions with total_amount confidence < 0.5 excluded from totals",
        },
    }
