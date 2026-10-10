"""Phase 3: evaluate on test and choose the confidence threshold on validation.

Writes outputs/metrics.json, outputs/confusion_matrix.png and outputs/threshold.json.
Test images are never used to choose anything.
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from config import CLASSES, IMG_SIZE, MODEL_VERSION, OUTPUTS_DIR, PROCESSED_DIR, SEED

THRESHOLDS = [round(0.40 + 0.05 * i, 2) for i in range(12)]  # 0.40 .. 0.95
TARGET_ACCEPTED_ACCURACY = 0.90
DEFAULT_THRESHOLD = 0.60


def predict(model, split):
    dataset = tf.keras.utils.image_dataset_from_directory(
        PROCESSED_DIR / split, image_size=(IMG_SIZE, IMG_SIZE), label_mode="categorical",
        batch_size=32, shuffle=False, seed=SEED, class_names=CLASSES)
    labels = np.concatenate([y.numpy() for _, y in dataset]).argmax(axis=1)
    return labels, model.predict(dataset, verbose=0)


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


def choose_threshold(sweep):
    for row in sweep:
        if row["accepted_accuracy"] is not None and row["accepted_accuracy"] >= TARGET_ACCEPTED_ACCURACY:
            return row["threshold"], "lowest threshold reaching the target on validation"
    return DEFAULT_THRESHOLD, "target not reached on validation; default used"


def plot_confusion(matrix):
    figure, axis = plt.subplots(figsize=(5, 4.4), dpi=150)
    image = axis.imshow(matrix, cmap="Blues", vmin=0)
    axis.set_xticks(range(len(CLASSES)), CLASSES)
    axis.set_yticks(range(len(CLASSES)), CLASSES)
    axis.set_xlabel("Predicción")
    axis.set_ylabel("Clase real")
    axis.set_title("Matriz de confusión (test)")
    for row in range(len(CLASSES)):
        for column in range(len(CLASSES)):
            dark = matrix[row, column] > matrix.max() / 2
            axis.text(column, row, int(matrix[row, column]), ha="center", va="center",
                      color="white" if dark else "black")
    for spine in axis.spines.values():
        spine.set_visible(False)
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    figure.savefig(OUTPUTS_DIR / "confusion_matrix.png")
    plt.close(figure)


def main():
    model = tf.keras.models.load_model(OUTPUTS_DIR / "model.keras")
    val_labels, val_probabilities = predict(model, "val")
    test_labels, test_probabilities = predict(model, "test")
    predicted = test_probabilities.argmax(axis=1)

    precision, recall, f1, support = precision_recall_fscore_support(
        test_labels, predicted, labels=range(len(CLASSES)), zero_division=0)
    matrix = confusion_matrix(test_labels, predicted, labels=range(len(CLASSES)))
    plot_confusion(matrix)

    sweep = [coverage(val_labels, val_probabilities, t) for t in THRESHOLDS]
    threshold, reason = choose_threshold(sweep)

    metrics = {
        "model_version": MODEL_VERSION,
        "test": {
            "images": int(len(test_labels)),
            "accuracy": round(float(accuracy_score(test_labels, predicted)), 4),
            "f1_macro": round(float(f1_score(test_labels, predicted, average="macro")), 4),
            "per_class": {
                label: {"precision": round(float(precision[i]), 4), "recall": round(float(recall[i]), 4),
                        "f1": round(float(f1[i]), 4), "support": int(support[i])}
                for i, label in enumerate(CLASSES)},
            "confusion_matrix": {"rows_true_columns_predicted": CLASSES, "values": matrix.tolist()},
        },
        "threshold": {
            "chosen": threshold,
            "reason": reason,
            "target_accepted_accuracy": TARGET_ACCEPTED_ACCURACY,
            "validation_sweep": sweep,
            "validation_accuracy_without_threshold": round(
                float((val_probabilities.argmax(axis=1) == val_labels).mean()), 4),
            "test_at_chosen": coverage(test_labels, test_probabilities, threshold),
        },
    }
    (OUTPUTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    (OUTPUTS_DIR / "threshold.json").write_text(
        json.dumps({"threshold": threshold, "model_version": MODEL_VERSION}) + "\n")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
