"""Phase 4: convert model.keras to TFLite and check the section 4 contract.

Writes outputs/model_fp32.tflite (reference), outputs/model.tflite (dynamic-range
quantization: int8 weights, float32 input/output) and outputs/model_io.json.
"""
import argparse
import json

import numpy as np
import tensorflow as tf

from config import CLASSES, IMG_SIZE, OUTPUTS_DIR


def describe(path):
    interpreter = tf.lite.Interpreter(model_path=str(path))
    interpreter.allocate_tensors()

    def details(tensor):
        return {"name": tensor["name"], "shape": tensor["shape"].tolist(),
                "dtype": np.dtype(tensor["dtype"]).name}

    return {"file": path.name, "bytes": path.stat().st_size,
            "inputs": [details(t) for t in interpreter.get_input_details()],
            "outputs": [details(t) for t in interpreter.get_output_details()]}


def main():
    # Every training run keeps its files in outputs/<run>/ (see 02_entrenar.py).
    global OUTPUTS_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="final")
    OUTPUTS_DIR = OUTPUTS_DIR / parser.parse_args().run

    model = tf.keras.models.load_model(OUTPUTS_DIR / "model.keras")

    # fp32 reference
    (OUTPUTS_DIR / "model_fp32.tflite").write_bytes(
        tf.lite.TFLiteConverter.from_keras_model(model).convert())

    # dynamic-range quantization: int8 weights, input/output stay float32
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    (OUTPUTS_DIR / "model.tflite").write_bytes(converter.convert())

    report = {name: describe(OUTPUTS_DIR / name) for name in ("model_fp32.tflite", "model.tflite")}
    for description in report.values():
        assert len(description["inputs"]) == 1 and len(description["outputs"]) == 1, description
        assert description["inputs"][0]["shape"] == [1, IMG_SIZE, IMG_SIZE, 3], description
        assert description["inputs"][0]["dtype"] == "float32", description
        assert description["outputs"][0]["shape"] == [1, len(CLASSES)], description
        assert description["outputs"][0]["dtype"] == "float32", description
    report["contract_ok"] = True
    (OUTPUTS_DIR / "model_io.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
