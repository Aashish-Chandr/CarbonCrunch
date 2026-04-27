"""
ocr_engine.py — EasyOCR wrapper with lazy initialisation.

Keeps a single Reader instance alive for the lifetime of the process
so model weights are loaded only once.
"""
import logging
from typing import List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_reader = None  # module-level singleton


def get_reader(languages: List[str], use_gpu: bool):
    """Return (and lazily create) the EasyOCR Reader singleton."""
    global _reader
    if _reader is None:
        import easyocr  # deferred import — not needed at import time
        logger.info("Loading EasyOCR model (languages=%s, gpu=%s)…", languages, use_gpu)
        _reader = easyocr.Reader(languages, gpu=use_gpu, verbose=False)
        logger.info("EasyOCR ready.")
    return _reader


def run_ocr(image: np.ndarray, cfg: dict) -> List[Tuple[str, float]]:
    """
    Run OCR on a preprocessed image.

    Parameters
    ----------
    image : np.ndarray
        Grayscale or BGR image array.
    cfg : dict
        Top-level pipeline config dict (uses cfg['ocr']).

    Returns
    -------
    List of (text, confidence) tuples, sorted top-to-bottom by bounding box.
    """
    ocr_cfg = cfg.get("ocr", {})
    reader = get_reader(
        languages=ocr_cfg.get("languages", ["en"]),
        use_gpu=ocr_cfg.get("use_gpu", False),
    )

    raw = reader.readtext(image, detail=1, paragraph=False)

    # Sort detections top-to-bottom (by y-centre of bounding box)
    def _y_centre(item):
        bbox = item[0]
        return (bbox[0][1] + bbox[2][1]) / 2

    raw_sorted = sorted(raw, key=_y_centre)

    results = [
        (text.strip(), float(conf))
        for (_, text, conf) in raw_sorted
        if text.strip()
    ]
    return results


def average_confidence(results: List[Tuple[str, float]]) -> float:
    """Mean OCR confidence across all detected text regions."""
    if not results:
        return 0.0
    return sum(c for _, c in results) / len(results)
