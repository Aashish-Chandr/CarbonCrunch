"""
pipeline.py — End-to-end receipt OCR pipeline.

Orchestrates:
  preprocessing → OCR → extraction → JSON output → summary
"""
import json
import logging
import os
from typing import List, Optional

from tqdm import tqdm

from .config import load_config, setup_logging
from .preprocessing import preprocess_image
from .ocr_engine import run_ocr, average_confidence
from .extractor import extract_all
from .summary import generate_summary

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _collect_images(folder: str) -> List[str]:
    """Return sorted list of image paths inside *folder*."""
    paths = []
    for fname in sorted(os.listdir(folder)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            paths.append(os.path.join(folder, fname))
    return paths


def _save_json(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Core processing ────────────────────────────────────────────────────────────

def process_single(image_path: str, cfg: dict) -> dict:
    """
    Run the full pipeline on one receipt image.

    Returns a structured dict ready to be serialised as JSON.
    """
    filename = os.path.basename(image_path)

    result: dict = {"filename": filename, "error": None}

    try:
        # 1. Preprocess
        preprocessed = preprocess_image(image_path, cfg["preprocessing"])

        # 2. OCR
        ocr_results = run_ocr(preprocessed, cfg)
        ocr_conf = average_confidence(ocr_results)

        # 3. Extract fields
        extracted = extract_all(ocr_results, ocr_conf, cfg)

        result.update(extracted)
        result["ocr_confidence"] = round(ocr_conf, 4)

    except Exception as exc:
        logger.error("Failed to process %s: %s", filename, exc, exc_info=True)
        result["error"] = str(exc)

    return result


def run_pipeline(
    config_path: Optional[str] = None,
    input_folder: Optional[str] = None,
    output_folder: Optional[str] = None,
) -> dict:
    """
    Run the pipeline over all images in *input_folder*.

    Parameters
    ----------
    config_path   : path to config.yaml (defaults to repo root config.yaml)
    input_folder  : override cfg['paths']['input_folder']
    output_folder : override cfg['paths']['output_folder']

    Returns
    -------
    The expense summary dict.
    """
    cfg = load_config(config_path) if config_path else load_config()
    setup_logging(cfg)

    in_dir = input_folder or cfg["paths"]["input_folder"]
    out_dir = output_folder or cfg["paths"]["output_folder"]
    os.makedirs(out_dir, exist_ok=True)

    image_paths = _collect_images(in_dir)
    if not image_paths:
        logger.warning("No images found in %s", in_dir)
        return {}

    logger.info("Processing %d receipt image(s)…", len(image_paths))

    all_receipts: List[dict] = []

    for img_path in tqdm(image_paths, desc="OCR", unit="img"):
        receipt = process_single(img_path, cfg)
        all_receipts.append(receipt)

        # Save individual JSON — derive stem from the receipt filename
        stem = os.path.splitext(os.path.basename(img_path))[0]
        out_path = os.path.join(out_dir, f"{stem}.json")
        _save_json(receipt, out_path)

    # Save combined JSON
    _save_json(all_receipts, os.path.join(out_dir, "all_receipts.json"))
    logger.info("Saved %d individual JSON files.", len(all_receipts))

    # Generate and save expense summary
    summary = generate_summary(all_receipts, cfg)
    _save_json(summary, os.path.join(out_dir, "expense_summary.json"))
    logger.info(
        "Summary: total_spend=%.2f, transactions=%d",
        summary["summary"]["total_spend"],
        summary["summary"]["number_of_transactions"],
    )

    return summary


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Receipt OCR Pipeline")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    parser.add_argument("--input", default=None, help="Input folder with receipt images")
    parser.add_argument("--output", default=None, help="Output folder for JSON results")
    args = parser.parse_args()

    run_pipeline(
        config_path=args.config,
        input_folder=args.input,
        output_folder=args.output,
    )
