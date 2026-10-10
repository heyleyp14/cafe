"""Phase 5: Keras vs TFLite parity and golden vectors for the Android tests.

Level 1: 100 test images through model.keras, model_fp32.tflite and model.tflite.
Level 2: 10 test images exported to outputs/golden/ as NN.jpg, NN.rgb and golden.json,
with probabilities from the model shipped in the app (config.APP_MODEL_FILE).
Writes outputs/parity.json (including PC latency, reference only).
"""
import json
import platform
import random
import shutil
import time

import numpy as np
import tensorflow as tf

from config import APP_MODEL_FILE, CLASSES, IMG_SIZE, OUTPUTS_DIR, PROCESSED_DIR, SEED

PARITY_IMAGES = 100
GOLDEN_PER_CLASS = {"minador": 3, "roya": 3, "sana": 4}  # 10 images, at least 2 per class
LATENCY_WARMUP, LATENCY_RUNS = 5, 50


def load_resized(path):
    """Same decode and squash resize as training (image_dataset_from_directory)."""
    image = tf.io.decode_jpeg(tf.io.read_file(str(path)), channels=3)
    return tf.image.resize(image, (IMG_SIZE, IMG_SIZE), method="bilinear").numpy()


class TFLiteModel:
    def __init__(self, path):
        self.interpreter = tf.lite.Interpreter(model_path=str(path))
        self.interpreter.allocate_tensors()
        self.input = self.interpreter.get_input_details()[0]["index"]
        self.output = self.interpreter.get_output_details()[0]["index"]

    def __call__(self, image):
        self.interpreter.set_tensor(self.input, image[None].astype(np.float32))
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output)[0]


def compare(reference, candidate):
    return {
        "argmax_agreement": round(float((reference.argmax(1) == candidate.argmax(1)).mean()), 4),
        "max_abs_probability_difference": round(float(np.abs(reference - candidate).max()), 6),
    }


def measure_latency(model, image):
    for _ in range(LATENCY_WARMUP):
        model(image)
    times = []
    for _ in range(LATENCY_RUNS):
        start = time.perf_counter()
        model(image)
        times.append((time.perf_counter() - start) * 1000)
    return {"median_ms": round(float(np.median(times)), 2), "p95_ms": round(float(np.percentile(times, 95)), 2)}


def export_golden(app_model, rng):
    golden_dir = OUTPUTS_DIR / "golden"
    shutil.rmtree(golden_dir, ignore_errors=True)
    golden_dir.mkdir(parents=True)
    entries, number = [], 0
    for label in CLASSES:
        files = sorted((PROCESSED_DIR / "test" / label).glob("*.jpg"))
        for path in rng.sample(files, GOLDEN_PER_CLASS[label]):
            name = f"{number:02d}"
            shutil.copyfile(path, golden_dir / f"{name}.jpg")
            rgb = np.clip(np.rint(load_resized(path)), 0, 255).astype(np.uint8)
            (golden_dir / f"{name}.rgb").write_bytes(rgb.tobytes())  # 224*224*3 raw RGB bytes
            # Probabilities come from the .rgb bytes: exactly what Android will feed the model.
            probabilities = app_model(rgb.astype(np.float32))
            entries.append({"file": name, "expected_class": label, "source": path.name,
                            "predicted_class": CLASSES[int(probabilities.argmax())],
                            "probs_tflite": [float(p) for p in probabilities]})
            number += 1
    (golden_dir / "golden.json").write_text(json.dumps(entries, indent=2) + "\n")
    return entries


def main():
    rng = random.Random(SEED)
    keras_model = tf.keras.models.load_model(OUTPUTS_DIR / "model.keras")
    fp32 = TFLiteModel(OUTPUTS_DIR / "model_fp32.tflite")
    quantized = TFLiteModel(OUTPUTS_DIR / "model.tflite")

    files = sorted((PROCESSED_DIR / "test").glob("*/*.jpg"))
    images = np.stack([load_resized(p) for p in rng.sample(files, PARITY_IMAGES)])
    keras_probabilities = keras_model.predict(images, verbose=0)
    fp32_probabilities = np.stack([fp32(image) for image in images])
    quantized_probabilities = np.stack([quantized(image) for image in images])

    # Golden probabilities must come from the model the app ships.
    golden = export_golden(TFLiteModel(OUTPUTS_DIR / APP_MODEL_FILE), rng)
    parity = {
        "images": PARITY_IMAGES,
        "keras_vs_fp32": compare(keras_probabilities, fp32_probabilities),
        "keras_vs_quantized": compare(keras_probabilities, quantized_probabilities),
        "fp32_vs_quantized": compare(fp32_probabilities, quantized_probabilities),
        "golden": {"model": APP_MODEL_FILE,
                   "images": len(golden),
                   "per_class": dict(GOLDEN_PER_CLASS),
                   "predicted_matches_expected": sum(g["predicted_class"] == g["expected_class"] for g in golden)},
        "pc_latency_reference_only": {
            "machine": platform.processor() or platform.machine(),
            "fp32": measure_latency(fp32, images[0]),
            "quantized": measure_latency(quantized, images[0]),
        },
    }
    (OUTPUTS_DIR / "parity.json").write_text(json.dumps(parity, indent=2) + "\n")
    print(json.dumps(parity, indent=2))


if __name__ == "__main__":
    main()
