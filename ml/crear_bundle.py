"""Creates the zips to upload to Colab/Kaggle. Works on Linux, macOS and Windows.

Without arguments: cafe_ml_bundle.zip (code only).
With --data: cafe_data_v2.zip (processed images and dataset_stats.json).
"""
import argparse
import zipfile

from config import ML_DIR, OUTPUTS_DIR, PROCESSED_DIR

FILES = ["config.py", "requirements.txt", "colab_run.py", "colab_run_v2.py",
         *sorted(p.name for p in ML_DIR.glob("0*.py"))]


def archive_name(path):
    """Path inside the zip: `ml/...` with forward slashes (Colab is Linux)."""
    return f"ml/{path.relative_to(ML_DIR).as_posix()}"


def create_code_bundle():
    target = ML_DIR.parent / "cafe_ml_bundle.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in FILES:
            bundle.write(ML_DIR / name, archive_name(ML_DIR / name))
    print(f"{target.name} listo ({len(FILES)} archivos)")


def create_data_bundle():
    """Only data/processed and the stats: never raw, external or final holdout images."""
    images = sorted(p for p in PROCESSED_DIR.rglob("*") if p.is_file())
    if not images:
        raise SystemExit(f"{PROCESSED_DIR} is empty: run 01_preparar_datos.py first")
    target = ML_DIR.parent / "cafe_data_v2.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_STORED) as bundle:  # JPEG does not compress further
        for path in [*images, OUTPUTS_DIR / "dataset_stats.json"]:
            bundle.write(path, archive_name(path))
    print(f"{target.name} listo ({len(images) + 1} archivos, {target.stat().st_size / 1e6:.1f} MB)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", action="store_true", help="write cafe_data_v2.zip instead of the code bundle")
    args = parser.parse_args()
    if args.data:
        create_data_bundle()
    else:
        create_code_bundle()


if __name__ == "__main__":
    main()
