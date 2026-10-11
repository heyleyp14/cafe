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

# Processed images are stored downscaled: longest side at most this many pixels.
PROCESSED_MAX_SIDE = 512
SOURCE_SEPARATOR = "__"


def processed_name(source, name):
    """File name of a processed image: `<source>__<name>.jpg`."""
    return f"{source}{SOURCE_SEPARATOR}{name}.jpg"


def source_of(path):
    """Dataset a processed image comes from, read from its file name."""
    return Path(path).name.split(SOURCE_SEPARATOR, 1)[0]


def list_processed(splits, exclude_source=None, only_source=None):
    """Sorted (paths, class indexes, sources) of the processed images in `splits`."""
    paths, labels, sources = [], [], []
    for split in splits:
        for index, label in enumerate(CLASSES):
            for path in sorted((PROCESSED_DIR / split / label).glob("*.jpg")):
                source = source_of(path)
                if source == exclude_source or (only_source is not None and source != only_source):
                    continue
                paths.append(str(path))
                labels.append(index)
                sources.append(source)
    return paths, labels, sources

# Shown by the app in "Acerca de" (contract, section 4).
MODEL_VERSION = "v2-2026-10"

# Model shipped in the app as assets/model.tflite. The float32 file is used because the
# dynamic-range one gives CPU-dependent probabilities (docs/decisiones.md, phase 8).
APP_MODEL_FILE = "model_fp32.tflite"
