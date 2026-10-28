"""Read-only bundled resources and durable per-user application files."""

import json
import logging
import os
from pathlib import Path
import shutil
import sys

try:
    from .schema import SCHEMA_VERSION, SEED_FILENAME
except ImportError:
    from schema import SCHEMA_VERSION, SEED_FILENAME

APP_NAME = "ToothGenderClassification"


def resource_path(*parts):
    installed = Path(__file__).resolve().parent / "resources"
    base = Path(
        getattr(
            sys,
            "_MEIPASS",
            installed if installed.exists() else Path(__file__).resolve().parent.parent,
        )
    )
    return base.joinpath(*parts)


def user_dir():
    override = os.environ.get("TOOTH_APP_DATA_DIR")
    if override:
        base = Path(override)
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / APP_NAME
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME
    # Preserve older clients' data while starting this schema with the v1 model.
    base = base / ("dataset-" + SCHEMA_VERSION)
    base.mkdir(parents=True, exist_ok=True)
    return base


def active_generation():
    pointer = user_dir() / "active-model.json"
    if not pointer.exists():
        return None
    generation = json.loads(pointer.read_text(encoding="utf-8"))["generation"]
    if (
        not isinstance(generation, str)
        or len(generation) != 32
        or any(c not in "0123456789abcdef" for c in generation)
    ):
        raise ValueError("Invalid active model reference.")
    folder = user_dir() / "generations" / generation
    if not all((folder / name).is_file() for name in ("pipeline.joblib", SEED_FILENAME)):
        raise ValueError("The active training dataset or model is missing.")
    return folder


def model_path():
    generation = active_generation()
    if generation:
        return generation / "pipeline.joblib"
    path = user_dir() / "pipeline.joblib"
    return path if path.exists() else resource_path("models", "current", "pipeline.joblib")


def dataset_path():
    generation = active_generation()
    if generation:
        return generation / SEED_FILENAME
    path = user_dir() / SEED_FILENAME
    if not path.exists():
        shutil.copy2(resource_path("data", "raw", SEED_FILENAME), path)
    return path


def configure_logging():
    path = user_dir() / "application.log"
    from logging.handlers import RotatingFileHandler

    logging.basicConfig(
        level=logging.INFO,
        handlers=[RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")],
    )
    return path
