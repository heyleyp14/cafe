"""Creates cafe_ml_bundle.zip (code only) for Colab/Kaggle. Works on Linux, macOS and Windows."""
import zipfile

from config import ML_DIR

FILES = ["config.py", "requirements.txt", "colab_run.py", *sorted(p.name for p in ML_DIR.glob("0*.py"))]


def main():
    target = ML_DIR.parent / "cafe_ml_bundle.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in FILES:
            bundle.write(ML_DIR / name, f"ml/{name}")  # forward slashes: Colab is Linux
    print(f"{target.name} listo ({len(FILES)} archivos)")


if __name__ == "__main__":
    main()
