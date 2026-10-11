"""Unattended Colab run for the four-class model (v3): EfficientNet-B0 only.

Step 1 trains without BRACOL and measures on it (validation by source, also gives the
threshold). Step 2 trains the final model with every source. Run from /content/ml after
extracting cafe_ml_bundle.zip and cafe_data_v2.zip at /content.
"""
import glob
import json
import os
import site
import subprocess
import sys
import time

ARCH = "efficientnetb0"
HOLDOUT = "bracol"


def say(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    say("installing pinned dependencies")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt",
                    "tensorflow[and-cuda]==2.21.0"], check=True)
    # TensorFlow needs the pip-installed CUDA libraries on the loader path.
    nvidia = [p for s in site.getsitepackages() for p in glob.glob(os.path.join(s, "nvidia", "*", "lib"))]
    env = dict(os.environ, LD_LIBRARY_PATH=":".join(nvidia + [os.environ.get("LD_LIBRARY_PATH", "")]))

    def run(*args):
        subprocess.run([sys.executable, *args], env=env, check=True)

    run("-c", "import tensorflow as tf; g = tf.config.list_physical_devices('GPU'); "
              "print('GPU:', g, flush=True); assert g, 'No GPU visible'")

    for name, extra in (("stage1_v3", ["--holdout-source", HOLDOUT]), ("final", [])):
        say(f"{name}: training {ARCH}" + (f" without {HOLDOUT}" if extra else " with every source"))
        run("02_entrenar.py", "--run", name, "--arch", ARCH, *extra)
        history = json.load(open(f"outputs/{name}/history.json"))
        val_loss = history["head"]["val_loss"] + history["finetune"]["val_loss"]
        assert min(val_loss) < val_loss[0], "validation loss never improved over epoch 1"
        say(f"{name}: TRAINED in {history['training']['seconds']} s, val_loss {val_loss[0]:.4f} -> {min(val_loss):.4f}")
        run("03_evaluar.py", "--run", name)
        metrics = json.load(open(f"outputs/{name}/metrics.json"))
        holdout = metrics.get("holdout_source")
        say(f"{name}: EVALUATED internal macro F1 {metrics['internal']['f1_macro']}"
            + (f", {HOLDOUT} macro F1 {holdout['f1_macro']}" if holdout else "")
            + f", threshold {metrics['threshold']['chosen']}")

    subprocess.run(["zip", "-q", "-r", "../cafe_outputs_v3.zip", "outputs/stage1_v3", "outputs/final",
                    "outputs/dataset_stats.json"], check=True)
    say("ALL DONE: /content/cafe_outputs_v3.zip")


if __name__ == "__main__":
    main()
