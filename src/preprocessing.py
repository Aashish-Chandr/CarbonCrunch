"""
preprocessing.py — Image preprocessing for receipt OCR.

Steps applied to every image:
  1. Resize (upscale narrow images)
  2. Deskew via Hough line detection
  3. Grayscale conversion
  4. CLAHE contrast enhancement
  5. Fast non-local means denoising
  6. Adaptive binarisation (Gaussian threshold)
"""
import logging
import numpy as np
import cv2
from PIL import Image

logger = logging.getLogger(__name__)


def preprocess_image(image_path: str, cfg: dict) -> np.ndarray:
    """
    Load and preprocess a receipt image.

    Parameters
    ----------
    image_path : str
        Absolute or relative path to the image file.
    cfg : dict
        The 'preprocessing' sub-dict from config.yaml.

    Returns
    -------
    np.ndarray
        Binarised grayscale image ready for OCR.
    """
    min_width = cfg.get("min_width", 800)
    clahe_clip = cfg.get("clahe_clip_limit", 2.0)
    clahe_tile = tuple(cfg.get("clahe_tile_grid", [8, 8]))
    denoise_h = cfg.get("denoise_h", 10)
    block_size = cfg.get("adaptive_block_size", 11)
    adaptive_c = cfg.get("adaptive_c", 2)

    try:
        img = cv2.imread(image_path)
        if img is None:
            # Fallback: PIL handles exotic formats (webp, tiff, etc.)
            pil_img = Image.open(image_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # ── 1. Upscale narrow images ──────────────────────────────────────
        h, w = img.shape[:2]
        if w < min_width:
            scale = min_width / w
            img = cv2.resize(img, None, fx=scale, fy=scale,
                             interpolation=cv2.INTER_CUBIC)

        # ── 2. Deskew ─────────────────────────────────────────────────────
        img = _deskew(img)

        # ── 3. Grayscale ──────────────────────────────────────────────────
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

        # ── 4. CLAHE contrast enhancement ────────────────────────────────
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_tile)
        gray = clahe.apply(gray)

        # ── 5. Denoise ────────────────────────────────────────────────────
        gray = cv2.fastNlMeansDenoising(gray, h=denoise_h)

        # ── 6. Adaptive binarisation ──────────────────────────────────────
        result = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size, adaptive_c,
        )
        return result

    except Exception as exc:
        logger.warning("Preprocessing failed for %s: %s — using raw grayscale", image_path, exc)
        pil = Image.open(image_path).convert("L")
        return np.array(pil)


# ── Private helpers ────────────────────────────────────────────────────────────

def _deskew(img: np.ndarray) -> np.ndarray:
    """Detect dominant line angle and rotate to correct skew."""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100,
                                minLineLength=100, maxLineGap=10)
        if lines is None:
            return img

        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if -45 < angle < 45:
                    angles.append(angle)

        if not angles:
            return img

        median_angle = float(np.median(angles))
        if abs(median_angle) <= 0.5:
            return img

        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), median_angle, 1.0)
        return cv2.warpAffine(img, M, (w, h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    except Exception as exc:
        logger.debug("Deskew skipped: %s", exc)
        return img
