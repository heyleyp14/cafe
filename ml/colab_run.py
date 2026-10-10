"""Unattended version of colab_entrenamiento.ipynb for the Colab CLI.

Runs phases 1 to 5 in order from /content/ml, checks each phase's acceptance
criteria and stops at the first failure. Progress goes to stdout (redirect to a log).
"""
import glob
import json
import os
import site
import subprocess
import sys
import time

ROCOLE = "https://data.mendeley.com/public-files/datasets/c5yvn32dzg/files"
DOWNLOADS = [
    ("data/raw/rocole/RoCoLE-json.json", f"{ROCOLE}/654cdf31-4ce6-4a15-b5cf-52a92181a698/file_downloaded", 2488394),
    ("data/raw/rocole/RoCoLe-voc.tar.gz", f"{ROCOLE}/3cfa348c-179b-4f05-9a6d-6c9343dd5c03/file_downloaded", 697591506),
    ("data/raw/decafia/CoffeeLeaf-CO.zip", "https://zenodo.org/records/19931904/files/CoffeeLeaf-CO.zip?download=1",
     208325327),
]


def say(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def shell(*command):
    subprocess.run(command, check=True)


def load(name):
    with open(f"outputs/{name}") as handle:
        return json.load(handle)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    say("installing pinned dependencies")
    shell(sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt", "tensorflow[and-cuda]==2.21.0")

    # TensorFlow needs the pip-installed CUDA libraries on the loader path.
    nvidia = [p for s in site.getsitepackages() for p in glob.glob(os.path.join(s, "nvidia", "*", "lib"))]
    env = dict(os.environ, LD_LIBRARY_PATH=":".join(nvidia + [os.environ.get("LD_LIBRARY_PATH", "")]))

    def run(*args):
        subprocess.run([sys.executable, *args], env=env, check=True)

    run("-c", "import tensorflow as tf; g = tf.config.list_physical_devices('GPU'); "
              "print('TensorFlow', tf.__version__, 'GPU:', g, flush=True); assert g, 'No GPU visible'")

    say("phase 1: downloading datasets")
    os.makedirs("data/raw/rocole", exist_ok=True)
    os.makedirs("data/raw/decafia", exist_ok=True)
    for path, url, size in DOWNLOADS:
        shell("curl", "-sSfL", "--retry", "8", "--retry-all-errors", "-C", "-", "-o", path, url)
        assert os.path.getsize(path) == size, f"incomplete download: {path}"
    shell("tar", "-xzf", "data/raw/rocole/RoCoLe-voc.tar.gz", "-C", "data/raw/rocole")
    shell("unzip", "-q", "-o", "data/raw/decafia/CoffeeLeaf-CO.zip", "-d", "data/raw/decafia")

    run("01_preparar_datos.py")
    stats = load("dataset_stats.json")
    assert all(v == 0 for v in stats["leakage_check"].values()), stats["leakage_check"]
    assert min(stats["counts"]["train"].values()) >= 100, stats["counts"]["train"]
    say(f"PHASE 1 ACCEPTED: {stats['final_images']} images, train {stats['counts']['train']}")

    say("phase 2: training")
    run("02_entrenar.py")
    history = load("history.json")
    for name in ("model.keras", "labels.txt", "history.json"):
        assert os.path.exists(f"outputs/{name}"), name
    val_loss = history["head"]["val_loss"] + history["finetune"]["val_loss"]
    assert min(val_loss) < val_loss[0], "validation loss never improved over epoch 1"
    say(f"PHASE 2 ACCEPTED: val_loss epoch 1 {val_loss[0]:.4f}, minimum {min(val_loss):.4f}")

    say("phase 3: evaluation")
    run("03_evaluar.py")
    for name in ("metrics.json", "confusion_matrix.png", "threshold.json"):
        assert os.path.exists(f"outputs/{name}"), name
    say("PHASE 3 ACCEPTED")

    say("phase 4: TFLite conversion")
    run("04_convertir_tflite.py")
    assert load("model_io.json")["contract_ok"]
    say("PHASE 4 ACCEPTED")

    say("phase 5: parity")
    run("05_paridad_tflite.py")
    assert os.path.exists("outputs/golden/golden.json")
    agreement = load("parity.json")["keras_vs_quantized"]["argmax_agreement"]
    say(f"PHASE 5 FILES GENERATED: Keras vs quantized class agreement {agreement} (expected >= 0.98)")

    shell("zip", "-q", "-r", "../cafe_outputs.zip", "outputs")
    say("ALL DONE: /content/cafe_outputs.zip")


if __name__ == "__main__":
    main()
