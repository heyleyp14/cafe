"""Shared configuration for the ML pipeline (plan section 3 and phase 0)."""
from pathlib import Path

# Alphabetical and fixed: this is the order of labels.txt (contract, section 4).
CLASSES = ["minador", "roya", "sana"]
IMG_SIZE = 224
SEED = 42

ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = ML_DIR / "outputs"
SPLITS = ("train", "val", "test")

# Shown by the app in "Acerca de" (contract, section 4).
MODEL_VERSION = "v1-2026-10"

# Model shipped in the app as assets/model.tflite. The float32 file is used because the
# dynamic-range one gives CPU-dependent probabilities (docs/decisiones.md, phase 8).
APP_MODEL_FILE = "model_fp32.tflite"
