"""Cross-validation of training variants: every processed image is tested exactly once.

Pools train, val and test of ml/data/processed (manifest.json), builds K group-aware
folds stratified by (source, class) and, per fold, trains a fresh EfficientNetB0 with
the recipe of 02_entrenar.py plus the knobs of the chosen variant. Test images are
always fed whole and squashed to the input size, as the app does.
Writes outputs/cv/<variant>.json and outputs/cv/<variant>_predicciones.csv.
"""
import argparse
import csv
import gc
import importlib
import json
import platform
import random
import time
from collections import defaultdict

import numpy as np

from config import CLASSES, IMG_SIZE, OUTPUTS_DIR, PROCESSED_DIR, SEED

prepare = importlib.import_module("01_preparar_datos")  # the module name starts with a digit

ARCH = "efficientnetb0"
# Knobs of 02_entrenar.py; a variant only lists what it changes.
DEFAULTS = {"img_size": IMG_SIZE, "batch_size": 32, "leaf_crop_probability": 0.0, "loss_name": "cce",
            "class_boost": None}
VARIANTS = {
    "baseline": {},
    "leafcrop": {"leaf_crop_probability": 0.5},
    # Batch size 32 at 320 px runs out of memory on a 6 GB GPU during fine-tuning.
    "res320": {"img_size": 320, "batch_size": 16},
    "boost": {"loss_name": "focal", "class_boost": {"arana_roja": 2.0}},
    "leafcrop_res320": {"leaf_crop_probability": 0.5, "img_size": 320, "batch_size": 16},
}
VALIDATION_FRACTION = 0.15  # of the groups outside the test fold; only used for early stopping
FOCUS_CLASS = "arana_roja"
BOOTSTRAP_RESAMPLES = 1000
CV_DIR = OUTPUTS_DIR / "cv"


def say(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def assign_folds(items, folds, seed):
    """Write `item["fold"]` (0..folds-1): group-aware, stratified by (source, class)."""
    prepare.split_by_group(items, fractions={fold: 1 / folds for fold in range(folds)}, seed=seed, key="fold")


def fold_partition(items, fold, seed):
    """(train, validation, test) of one fold; validation is a group-aware part of the rest."""
    test = [item for item in items if item["fold"] == fold]
    rest = [item for item in items if item["fold"] != fold]
    prepare.split_by_group(rest, fractions={"train": 1 - VALIDATION_FRACTION, "val": VALIDATION_FRACTION},
                           seed=seed + 1 + fold, key="role")
    return ([item for item in rest if item["role"] == "train"],
            [item for item in rest if item["role"] == "val"], test)


def limit_groups(items, groups_per_stratum, seed):
    """Debugging only: the items of `groups_per_stratum` whole groups per (source, class)."""
    by_stratum = defaultdict(set)
    for item in items:
        by_stratum[prepare.stratum(item)].add(item["group"])
    kept = set()
    for key in sorted(by_stratum):
        groups = sorted(by_stratum[key])
        random.Random(seed).shuffle(groups)
        kept.update(groups[:groups_per_stratum])
    return [item for item in items if item["group"] in kept]


def bootstrap_interval(labels, predicted, class_index, seed, resamples=BOOTSTRAP_RESAMPLES):
    """95 % percentile interval of recall, precision and F1 of one class."""
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(labels), size=(resamples, len(labels)))
    is_class, called = (labels == class_index)[draws], (predicted == class_index)[draws]
    hits = (is_class & called).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):  # a resample without the class counts as 0
        values = {"recall": np.nan_to_num(hits / is_class.sum(axis=1)),
                  "precision": np.nan_to_num(hits / called.sum(axis=1)),
                  "f1": np.nan_to_num(2 * hits / (is_class.sum(axis=1) + called.sum(axis=1)))}
    return {name: [round(float(bound), 4) for bound in np.percentile(sample, [2.5, 97.5])]
            for name, sample in values.items()}


def spread(values):
    return {"mean": round(float(np.mean(values)), 4),
            "std": round(float(np.std(values, ddof=1)), 4) if len(values) > 1 else None}


def run_fold(training, settings, parts, args, fold):
    """Train on one fold and return (test probabilities, epochs run, seconds, peak GPU MiB)."""
    import tensorflow as tf

    train, validation, test = parts
    tf.keras.utils.set_random_seed(args.seed + fold)

    def lists(part):
        return ([str(PROCESSED_DIR / item["file"]) for item in part],
                [CLASSES.index(item["label"]) for item in part])

    train_paths, train_labels = lists(train)
    weights, _, _ = training.stratum_weights(train_labels, [item["source"] for item in train],
                                             class_boost=settings["class_boost"])
    train_ds = training.make_train_dataset(
        train_paths, train_labels, weights, img_size=settings["img_size"], batch_size=settings["batch_size"],
        leaf_boxes=[item["leaf_box"] for item in train],
        leaf_crop_probability=settings["leaf_crop_probability"])

    def evaluation(part):  # whole image squashed to the input size, as in the app
        return training.make_eval_dataset(*lists(part), img_size=settings["img_size"],
                                          batch_size=settings["batch_size"])

    gpu = bool(tf.config.list_physical_devices("GPU"))
    if gpu:
        tf.config.experimental.reset_memory_stats("GPU:0")
    started = time.time()
    model, base = training.build_model(ARCH, settings["img_size"])
    head, finetune = training.train(model, base, train_ds, evaluation(validation), args.epochs_head,
                                    args.epochs_finetune, loss=settings["loss_name"], verbose=args.keras_verbose)
    probabilities = model.predict(evaluation(test), verbose=0)
    epochs = {"head": len(head["loss"]), "finetune": len(finetune["loss"])}
    # Memory TensorFlow really used, not what it reserved.
    peak = round(tf.config.experimental.get_memory_info("GPU:0")["peak"] / 2**20) if gpu else None

    del model, base, train_ds
    tf.keras.backend.clear_session()
    gc.collect()
    return probabilities, epochs, time.time() - started, peak


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    parser.add_argument("--folds", type=int, default=3)
    parser.add_argument("--epochs-head", type=int, default=6)
    parser.add_argument("--epochs-finetune", type=int, default=25)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--limit", type=int, default=None,
                        help="debugging only: use this many groups per (source, class)")
    parser.add_argument("--batch-size", type=int, default=None, help="overrides the batch size of the variant")
    parser.add_argument("--keras-verbose", type=int, default=0, help="2 prints one line per epoch")
    args = parser.parse_args()

    manifest_file = PROCESSED_DIR / "manifest.json"
    if not manifest_file.exists():
        raise SystemExit(f"{manifest_file} not found: run 01_preparar_datos.py first")
    items = json.loads(manifest_file.read_text())
    if args.limit is not None:
        items = limit_groups(items, args.limit, args.seed)
    assign_folds(items, args.folds, args.seed)

    settings = {**DEFAULTS, **VARIANTS[args.variant]}
    if args.batch_size is not None:
        settings["batch_size"] = args.batch_size

    import tensorflow as tf
    training = importlib.import_module("02_entrenar")
    summarize = importlib.import_module("03_evaluar").summarize  # same metrics as metrics.json

    say(f"variant {args.variant}: {len(items)} images, {args.folds} folds, {json.dumps(settings)}")
    started = time.time()
    labels = np.array([CLASSES.index(item["label"]) for item in items])
    probabilities = np.zeros((len(items), len(CLASSES)), np.float32)
    position = {item["file"]: index for index, item in enumerate(items)}
    per_fold = []
    for fold in range(args.folds):
        parts = fold_partition(items, fold, args.seed)
        fold_probabilities, epochs, seconds, gpu_peak = run_fold(training, settings, parts, args, fold)
        rows = [position[item["file"]] for item in parts[2]]
        probabilities[rows] = fold_probabilities
        metrics = summarize(labels[rows], fold_probabilities)
        per_fold.append({"fold": fold,
                         "images": {name: len(part) for name, part in zip(("train", "val", "test"), parts)},
                         "accuracy": metrics["accuracy"], "f1_macro": metrics["f1_macro"],
                         "per_class": metrics["per_class"], "seconds": round(seconds, 1), "epochs_run": epochs,
                         "gpu_peak_mib": gpu_peak})
        say(f"fold {fold + 1}/{args.folds}: train {len(parts[0])}, val {len(parts[1])}, test {len(parts[2])} | "
            f"epochs {epochs['head']}+{epochs['finetune']} | accuracy {metrics['accuracy']:.4f}, "
            f"F1 macro {metrics['f1_macro']:.4f}, {FOCUS_CLASS} F1 {metrics['per_class'][FOCUS_CLASS]['f1']:.4f} | "
            f"{seconds:.0f} s")

    predicted = probabilities.argmax(axis=1)
    sources = np.array([item["source"] for item in items])
    pooled = summarize(labels, probabilities)
    pooled["by_source"] = {source: summarize(labels[sources == source], probabilities[sources == source])
                           for source in sorted(set(sources))}
    pooled[f"{FOCUS_CLASS}_ci95"] = {
        "method": f"percentile bootstrap, {BOOTSTRAP_RESAMPLES} resamples of the pooled predictions, seed {args.seed}",
        **bootstrap_interval(labels, predicted, CLASSES.index(FOCUS_CLASS), args.seed)}

    total_seconds = time.time() - started
    result = {
        "variant": args.variant,
        "settings": {"arch": ARCH, **settings, "epochs_head": args.epochs_head,
                     "epochs_finetune": args.epochs_finetune, "seed": args.seed, "limit": args.limit,
                     "validation_fraction": VALIDATION_FRACTION,
                     "evaluation": "whole image squashed to img_size (bilinear), never cropped"},
        "folds": args.folds,
        "images": len(items),
        "per_fold": per_fold,
        "pooled": pooled,
        "across_folds": {"std": "sample standard deviation (ddof = 1)",
                         f"{FOCUS_CLASS}_f1": spread([fold["per_class"][FOCUS_CLASS]["f1"] for fold in per_fold]),
                         "f1_macro": spread([fold["f1_macro"] for fold in per_fold])},
        "hardware": {
            "gpu": [tf.config.experimental.get_device_details(gpu).get("device_name")
                    for gpu in tf.config.list_physical_devices("GPU")],
            "tensorflow": tf.__version__,
            "keras": tf.keras.__version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "seconds": round(total_seconds, 1),
        },
    }
    CV_DIR.mkdir(parents=True, exist_ok=True)
    (CV_DIR / f"{args.variant}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    with open(CV_DIR / f"{args.variant}_predicciones.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "source", "label", "fold", "predicted", "confidence"])
        for item, row in zip(items, probabilities):
            writer.writerow([item["file"], item["source"], item["label"], item["fold"],
                             CLASSES[int(row.argmax())], f"{float(row.max()):.4f}"])

    focus = pooled["per_class"][FOCUS_CLASS]
    say(f"{args.variant} done: {len(items)} images tested once | accuracy {pooled['accuracy']:.4f}, "
        f"F1 macro {pooled['f1_macro']:.4f} | {FOCUS_CLASS} recall {focus['recall']:.4f}, "
        f"precision {focus['precision']:.4f}, F1 {focus['f1']:.4f} | {total_seconds:.0f} s")


if __name__ == "__main__":
    main()
