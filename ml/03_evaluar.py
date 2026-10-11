"""Phase 3 (model v2): evaluate a training run and choose the confidence threshold.

Reads outputs/<run>/model.keras and writes metrics.json, confusion_matrix.png and
threshold.json next to it. "Internal" images are the ones whose source took part in
the training; a holdout source, when the run has one, is evaluated whole ("validation
by source", plan v2 R1) and is the data the threshold is chosen with. The internal
test images are never used to choose anything.
"""
import argparse
import importlib
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from config import CLASSES, MODEL_VERSION, OUTPUTS_DIR, SPLITS, list_processed

training = importlib.import_module("02_entrenar")  # same decode and resize as training

THRESHOLDS = [round(0.40 + 0.05 * i, 2) for i in range(12)]  # 0.40 .. 0.95
TARGET_ACCEPTED_ACCURACY = 0.90
MIN_ACCEPTED_FRACTION = 0.50  # fallback rule only
CALIBRATION_BINS = 15


def predict(model, paths, labels):
    dataset = training.make_dataset(paths, labels)
    return np.asarray(labels), model.predict(dataset, verbose=0)


def summarize(labels, probabilities):
    """Accuracy, per-class metrics, macro F1 and confusion matrix of one set of images."""
    predicted = probabilities.argmax(axis=1)
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predicted, labels=range(len(CLASSES)), zero_division=0)
    matrix = confusion_matrix(labels, predicted, labels=range(len(CLASSES)))
    # A source may lack a class (RoCoLe has no minador): the macro average only covers
    # the classes that have images, otherwise an absent class would count as F1 = 0.
    present = [i for i in range(len(CLASSES)) if support[i] > 0]
    return {
        "images": int(len(labels)),
        "accuracy": round(float(accuracy_score(labels, predicted)), 4),
        "f1_macro": round(float(np.mean([f1[i] for i in present])), 4),
        "f1_macro_classes": [CLASSES[i] for i in present],
        "per_class": {
            label: {"precision": round(float(precision[i]), 4), "recall": round(float(recall[i]), 4),
                    "f1": round(float(f1[i]), 4), "support": int(support[i])}
            for i, label in enumerate(CLASSES)},
        "confusion_matrix": {"rows_true_columns_predicted": CLASSES, "values": matrix.tolist()},
    }


def calibration(labels, probabilities):
    """Expected calibration error over equal-width confidence bins."""
    confidence = probabilities.max(axis=1)
    correct = probabilities.argmax(axis=1) == labels
    bins = np.minimum((confidence * CALIBRATION_BINS).astype(int), CALIBRATION_BINS - 1)
    error = 0.0
    for index in range(CALIBRATION_BINS):
        inside = bins == index
        if inside.any():
            error += inside.mean() * abs(correct[inside].mean() - confidence[inside].mean())
    return {
        "images": int(len(labels)),
        "bins": CALIBRATION_BINS,
        "expected_calibration_error": round(float(error), 4),
        "mean_confidence": round(float(confidence.mean()), 4),
        "accuracy": round(float(correct.mean()), 4),
    }


def coverage(labels, probabilities, threshold):
    """Fraction of images accepted at `threshold` and accuracy over the accepted ones."""
    accepted = probabilities.max(axis=1) >= threshold
    correct = probabilities.argmax(axis=1) == labels
    return {
        "threshold": threshold,
        "accepted": int(accepted.sum()),
        "accepted_fraction": round(float(accepted.mean()), 4),
        "accepted_accuracy": round(float(correct[accepted].mean()), 4) if accepted.any() else None,
    }


def choose_threshold(sweep, selection):
    for row in sweep:
        if row["accepted_accuracy"] is not None and row["accepted_accuracy"] >= TARGET_ACCEPTED_ACCURACY:
            return row["threshold"], f"lowest threshold reaching the target on {selection}"
    usable = [row for row in sweep
              if row["accepted_accuracy"] is not None and row["accepted_fraction"] >= MIN_ACCEPTED_FRACTION]
    if usable:
        best = max(usable, key=lambda row: (row["accepted_accuracy"], -row["threshold"]))
        return best["threshold"], (
            f"target NOT reached on {selection}; highest accepted accuracy "
            f"({best['accepted_accuracy']}) among thresholds accepting at least "
            f"{MIN_ACCEPTED_FRACTION:.0%} of the images")
    return sweep[0]["threshold"], (
        f"target NOT reached on {selection} and no threshold accepts at least "
        f"{MIN_ACCEPTED_FRACTION:.0%} of the images; lowest threshold used")


def plot_confusion(matrix, target):
    figure, axis = plt.subplots(figsize=(5, 4.4), dpi=150)
    image = axis.imshow(matrix, cmap="Blues", vmin=0)
    axis.set_xticks(range(len(CLASSES)), CLASSES)
    axis.set_yticks(range(len(CLASSES)), CLASSES)
    axis.set_xlabel("Predicción")
    axis.set_ylabel("Clase real")
    axis.set_title("Matriz de confusión (test interno)")
    for row in range(len(CLASSES)):
        for column in range(len(CLASSES)):
            dark = matrix[row, column] > matrix.max() / 2
            axis.text(column, row, int(matrix[row, column]), ha="center", va="center",
                      color="white" if dark else "black")
    for spine in axis.spines.values():
        spine.set_visible(False)
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    figure.savefig(target)
    plt.close(figure)


def resolve_holdout(requested, trained_with, run):
    """The holdout source must be the one the run was trained without."""
    if requested is not None and requested != trained_with:
        raise SystemExit(f"--holdout-source {requested} does not match run '{run}', "
                         f"trained with holdout source {trained_with}")
    return trained_with


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="default", help="reads and writes outputs/<run>/")
    parser.add_argument("--holdout-source", default=None,
                        help="defaults to the one recorded in history.json; must match it")
    args = parser.parse_args()

    run_dir = OUTPUTS_DIR / args.run
    if not (run_dir / "model.keras").exists():
        raise SystemExit(f"{run_dir / 'model.keras'} not found: run 02_entrenar.py --run {args.run} first")
    trained = json.loads((run_dir / "history.json").read_text())["training"]
    holdout = resolve_holdout(args.holdout_source, trained["holdout_source"], args.run)

    model = tf.keras.models.load_model(run_dir / "model.keras")
    test_paths, test_labels, test_sources = list_processed(["test"], exclude_source=holdout)
    test_labels, test_probabilities = predict(model, test_paths, test_labels)
    test_sources = np.array(test_sources)

    internal = summarize(test_labels, test_probabilities)
    plot_confusion(np.array(internal["confusion_matrix"]["values"]), run_dir / "confusion_matrix.png")
    by_source = {source: summarize(test_labels[test_sources == source], test_probabilities[test_sources == source])
                 for source in sorted(set(test_sources))}
    calibrations = {"internal_test": calibration(test_labels, test_probabilities), "holdout_source": None}

    holdout_metrics = None
    if holdout is not None:
        # Every image of the source: none of them was used to train or to stop training.
        paths, labels, _ = list_processed(SPLITS, only_source=holdout)
        if not paths:
            raise SystemExit(f"No processed images for holdout source {holdout}")
        selection_labels, selection_probabilities = predict(model, paths, labels)
        selection = f"holdout source {holdout}"
        holdout_metrics = {"source": holdout, **summarize(selection_labels, selection_probabilities)}
        calibrations["holdout_source"] = calibration(selection_labels, selection_probabilities)
    else:
        paths, labels, _ = list_processed(["val"])
        selection_labels, selection_probabilities = predict(model, paths, labels)
        selection = "internal validation"

    sweep = [coverage(selection_labels, selection_probabilities, t) for t in THRESHOLDS]
    threshold, reason = choose_threshold(sweep, selection)

    metrics = {
        "model_version": MODEL_VERSION,
        "run": args.run,
        "arch": trained["arch"],
        "internal": internal,
        "by_source": by_source,
        "holdout_source": holdout_metrics,
        "calibration": calibrations,
        "threshold": {
            "chosen": threshold,
            "reason": reason,
            "selection_data": selection,
            "selection_images": int(len(selection_labels)),
            "target_accepted_accuracy": TARGET_ACCEPTED_ACCURACY,
            "selection_sweep": sweep,
            "selection_accuracy_without_threshold": round(
                float((selection_probabilities.argmax(axis=1) == selection_labels).mean()), 4),
            "internal_test_at_chosen": coverage(test_labels, test_probabilities, threshold),
        },
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    (run_dir / "threshold.json").write_text(
        json.dumps({"threshold": threshold, "model_version": MODEL_VERSION}) + "\n")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
