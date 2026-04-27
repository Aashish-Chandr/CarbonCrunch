"""
config.py — Load and expose pipeline configuration from config.yaml.
"""
import os
import yaml
import logging

_DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")


def load_config(path: str = _DEFAULT_CONFIG_PATH) -> dict:
    """Load YAML config and return as a plain dict."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def setup_logging(cfg: dict) -> None:
    """Configure root logger from config."""
    log_cfg = cfg.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
    fmt = log_cfg.get("format", "%(asctime)s | %(levelname)s | %(message)s")
    logging.basicConfig(level=level, format=fmt)
