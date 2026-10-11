"""Evaluates the frozen app model on the untouched final holdout (JMuBEN). Run it once.

The archives in data/final_holdout/jmuben are extracted on first use. Nothing measured here
may be used to change the model, the threshold or the data.
"""
import argparse
import json
import zipfile

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from config import APP_MODEL_FILE, CLASSES, DATA_DIR, IMG_SIZE, OUTPUTS_DIR

HOLDOUT_DIR = DATA_DIR / "final_holdout" / "jmuben"
# Folder name fragments of the published archives -> our classes.
FOLDER_TO_CLASS = {"leaf rust": "roya", "healthy": "sana", "miner": "minador"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def extract():
    target = HOLDOUT_DIR / "extracted"
    if not target.exists():
        for archive in sorted(HOLDOUT_DIR.glob("*.zip")):
            zipfile.ZipFile(archive).extractall(target)
    return target


def list_images(root):
    items = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        folder = " ".join(part.lower() for part in path.relative_to(root).parts[:-1])
        labels = {label for fragment, label in FOLDER_TO_CLASS.items() if fragment in folder}
        if len(labels) == 1:
            items.append((path, labels.pop()))
    return items


def expected_calibration_error(confidence, correct, bins=15):
    edges = np.linspace(0, 1, bins + 1)
    error = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        inside = (confidence > low) & (confidence <= high)
        if inside.any():
            error += inside.mean() * abs(correct[inside].mean() - confidence[inside].mean())
    return float(error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="final")
    run_dir = OUTPUTS_DIR / parser.parse_args().run
    threshold = json.loads((run_dir / "threshold.json").read_text())["threshold"]

    interpreter = tf.lite.Interpreter(model_path=str(run_dir / APP_MODEL_FILE), num_threads=8)
    interpreter.allocate_tensors()
    input_index = interpreter.get_input_details()[0]["index"]
    output_index = interpreter.get_output_details()[0]["index"]

    items = list_images(extract())
    labels, probabilities, unreadable = [], [], 0
    for path, label in items:
        try:
            image = tf.io.decode_image(tf.io.read_file(str(path)), channels=3, expand_animations=False)
        except tf.errors.InvalidArgumentError:
            unreadable += 1
            continue
        resized = tf.image.resize(image, (IMG_SIZE, IMG_SIZE), method="bilinear").numpy()
        interpreter.set_tensor(input_index, resized[None].astype(np.float32))
        interpreter.invoke()
        probabilities.append(interpreter.get_tensor(output_index)[0].copy())
        labels.append(CLASSES.index(label))

    labels, probabilities = np.array(labels), np.array(probabilities)
    predicted, confidence = probabilities.argmax(axis=1), probabilities.max(axis=1)
    correct = predicted == labels
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predicted, labels=range(len(CLASSES)), zero_division=0)
    accepted = confidence >= threshold
    report = {
        "dataset": "JMuBEN and JMuBEN2 (Mendeley t2r6rszp5c and tgv3zb82nd, CC BY 4.0): Leaf rust, Healthy, Miner",
        "model": f"{run_dir.name}/{APP_MODEL_FILE}",
        "images": int(len(labels)),
        "unreadable": unreadable,
        "accuracy": round(float(accuracy_score(labels, predicted)), 4),
        "f1_macro": round(float(f1_score(labels, predicted, average="macro")), 4),
        "per_class": {
            label: {"precision": round(float(precision[i]), 4), "recall": round(float(recall[i]), 4),
                    "f1": round(float(f1[i]), 4), "support": int(support[i])}
            for i, label in enumerate(CLASSES)},
        "confusion_matrix": {"rows_true_columns_predicted": CLASSES,
                             "values": confusion_matrix(labels, predicted, labels=range(len(CLASSES))).tolist()},
        "expected_calibration_error": round(expected_calibration_error(confidence, correct), 4),
        "mean_confidence": round(float(confidence.mean()), 4),
        "at_threshold": {"threshold": threshold, "accepted_fraction": round(float(accepted.mean()), 4),
                         "accepted_accuracy": round(float(correct[accepted].mean()), 4) if accepted.any() else None},
    }
    (run_dir / "final_holdout.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
