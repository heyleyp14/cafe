"""Unattended training of model v2 for the Colab CLI (docs/PLAN_reentrenamiento_v2.md, R4).

Run from /content/ml after extracting cafe_ml_bundle.zip and cafe_data_v2.zip at /content.
The data come already prepared (01_preparar_datos.py runs on the PC), so nothing is downloaded.

Stage 1 (default): trains both architectures WITHOUT BRACOL and evaluates them on it
("validation by source"); the architecture is chosen by that macro F1.
Stage 2 (`--stage 2 --arch <name>`): trains the final model with every source as run `final`.
Progress goes to stdout (redirect to a log); it stops at the first failure.
"""
import argparse
import glob
import json
import os
import site
import subprocess
import sys
import time

ARCHITECTURES = ("mobilenetv2", "efficientnetb0")
HOLDOUT_SOURCE = "bracol"
SPLITS = ("train", "val", "test")


def say(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def shell(*command):
    subprocess.run(command, check=True)


def load(run, name):
    with open(f"outputs/{run}/{name}") as handle:
        return json.load(handle)


def count_processed():
    """Images per split and source, read from the file names (`<source>__<name>.jpg`)."""
    counts = {}
    for split in SPLITS:
        files = glob.glob(f"data/processed/{split}/*/*.jpg")
        assert files, f"data/processed/{split} is empty: extract cafe_data_v2.zip at /content"
        counts[split] = {}
        for path in files:
            source = os.path.basename(path).split("__", 1)[0]
            counts[split][source] = counts[split].get(source, 0) + 1
    return counts


def train_and_evaluate(run, run_name, arch, holdout_source):
    holdout = ["--holdout-source", holdout_source] if holdout_source else []

    say(f"{run_name}: training {arch}" + (f" without {holdout_source}" if holdout_source else " with every source"))
    run("02_entrenar.py", "--run", run_name, "--arch", arch, *holdout)
    for name in ("model.keras", "labels.txt", "history.json"):
        assert os.path.exists(f"outputs/{run_name}/{name}"), name
    history = load(run_name, "history.json")
    val_loss = history["head"]["val_loss"] + history["finetune"]["val_loss"]
    assert min(val_loss) < val_loss[0], f"{run_name}: validation loss never improved over epoch 1"
    say(f"{run_name}: TRAINED in {history['training']['seconds']} s, epochs {history['training']['epochs_run']}, "
        f"val_loss epoch 1 {val_loss[0]:.4f}, minimum {min(val_loss):.4f}")

    say(f"{run_name}: evaluation")
    run("03_evaluar.py", "--run", run_name, *holdout)
    for name in ("metrics.json", "confusion_matrix.png", "threshold.json"):
        assert os.path.exists(f"outputs/{run_name}/{name}"), name
    metrics = load(run_name, "metrics.json")
    line = f"{run_name}: EVALUATED internal test macro F1 {metrics['internal']['f1_macro']}"
    if holdout_source:
        line += (f", {holdout_source} (holdout source, {metrics['holdout_source']['images']} images) "
                 f"macro F1 {metrics['holdout_source']['f1_macro']}")
    say(f"{line}, threshold {metrics['threshold']['chosen']}")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, choices=(1, 2), default=1)
    parser.add_argument("--arch", choices=ARCHITECTURES, help="stage 2 only: the architecture chosen in stage 1")
    args = parser.parse_args()
    if (args.stage == 2) != (args.arch is not None):
        parser.error("--arch is required with --stage 2 and only valid there")

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    say("installing pinned dependencies")
    shell(sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt", "tensorflow[and-cuda]==2.21.0")

    # TensorFlow needs the pip-installed CUDA libraries on the loader path.
    nvidia = [p for s in site.getsitepackages() for p in glob.glob(os.path.join(s, "nvidia", "*", "lib"))]
    env = dict(os.environ, LD_LIBRARY_PATH=":".join(nvidia + [os.environ.get("LD_LIBRARY_PATH", "")]))

    def run(*arguments):
        subprocess.run([sys.executable, *arguments], env=env, check=True)

    run("-c", "import tensorflow as tf; g = tf.config.list_physical_devices('GPU'); "
              "print('TensorFlow', tf.__version__, 'GPU:', g, flush=True); assert g, 'No GPU visible'")

    assert os.path.isdir("data/processed"), "data/processed not found: extract cafe_data_v2.zip at /content"
    assert os.path.exists("outputs/dataset_stats.json"), "outputs/dataset_stats.json not found"
    counts = count_processed()
    say(f"data ready: {sum(sum(c.values()) for c in counts.values())} images, by split and source {counts}")

    if args.stage == 1:
        results = {}
        for arch in ARCHITECTURES:
            metrics = train_and_evaluate(run, f"stage1_{arch}", arch, HOLDOUT_SOURCE)
            results[arch] = metrics["holdout_source"]["f1_macro"]
        say(f"STAGE 1 DONE: {HOLDOUT_SOURCE} macro F1 by architecture {results}")
    else:
        train_and_evaluate(run, "final", args.arch, None)
        say(f"STAGE 2 DONE: final model trained with {args.arch}")

    shell("zip", "-q", "-r", "../cafe_outputs_v2.zip", "outputs")
    say("ALL DONE: /content/cafe_outputs_v2.zip")


if __name__ == "__main__":
    main()
