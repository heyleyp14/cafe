"""Phase 2: train MobileNetV2 (head, then fine-tuning) on data/processed.

Writes outputs/model.keras, outputs/labels.txt and outputs/history.json.
The model follows the section 4 contract: float32 RGB 0-255 input, normalization inside.
"""
import argparse
import json
import platform
import time

import tensorflow as tf

from config import CLASSES, IMG_SIZE, OUTPUTS_DIR, PROCESSED_DIR, SEED

BATCH_SIZE = 32
FINE_TUNE_LAYERS = 30


def load(split, shuffle):
    return tf.keras.utils.image_dataset_from_directory(
        PROCESSED_DIR / split, image_size=(IMG_SIZE, IMG_SIZE),  # squash by default
        label_mode="categorical", batch_size=BATCH_SIZE, shuffle=shuffle,
        seed=SEED, class_names=CLASSES)


def build_model():
    base = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet")
    base.trainable = False

    inputs = tf.keras.Input((IMG_SIZE, IMG_SIZE, 3))  # float32 0..255
    x = tf.keras.layers.Rescaling(1 / 127.5, offset=-1)(inputs)  # normalization INSIDE the model
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(x)
    return tf.keras.Model(inputs, outputs), base


def class_weights():
    """Inverse-frequency weights from the training counts written by phase 1."""
    counts = json.loads((OUTPUTS_DIR / "dataset_stats.json").read_text())["counts"]["train"]
    total = sum(counts.values())
    return {i: total / (len(CLASSES) * counts[label]) for i, label in enumerate(CLASSES)}


def fit(model, train_ds, val_ds, learning_rate, epochs, weights):
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate),
                  loss="categorical_crossentropy", metrics=["accuracy"])
    stop = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True)
    return model.fit(train_ds, validation_data=val_ds, epochs=epochs,
                     class_weight=weights, callbacks=[stop]).history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs-head", type=int, default=15)
    parser.add_argument("--epochs-finetune", type=int, default=10)
    args = parser.parse_args()

    tf.keras.utils.set_random_seed(SEED)
    train_ds, val_ds = load("train", True), load("val", False)

    # Augmentation lives in the data pipeline only; it is NOT part of the exported model.
    augment = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomBrightness(0.2, value_range=(0, 255)),
        tf.keras.layers.RandomContrast(0.2),
    ])
    train_ds = (train_ds.map(lambda x, y: (augment(x, training=True), y),
                             num_parallel_calls=tf.data.AUTOTUNE)
                .prefetch(tf.data.AUTOTUNE))
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    model, base = build_model()
    weights = class_weights()
    started = time.time()

    # Stage A: train the head with the base frozen.
    head = fit(model, train_ds, val_ds, 1e-3, args.epochs_head, weights)

    # Stage B: unfreeze the last layers of the base, keeping every BatchNormalization frozen.
    base.trainable = True
    for layer in base.layers[:-FINE_TUNE_LAYERS]:
        layer.trainable = False
    for layer in base.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
    finetune = fit(model, train_ds, val_ds, 1e-5, args.epochs_finetune, weights)

    seconds = time.time() - started
    OUTPUTS_DIR.mkdir(exist_ok=True)
    model.save(OUTPUTS_DIR / "model.keras")
    (OUTPUTS_DIR / "labels.txt").write_text("\n".join(CLASSES) + "\n")

    gpus = tf.config.list_physical_devices("GPU")
    history = {
        "head": head,
        "finetune": finetune,
        "class_weight": {CLASSES[i]: w for i, w in weights.items()},
        "training": {
            "seconds": round(seconds, 1),
            "epochs_requested": {"head": args.epochs_head, "finetune": args.epochs_finetune},
            "epochs_run": {"head": len(head["loss"]), "finetune": len(finetune["loss"])},
            "tensorflow": tf.__version__,
            "keras": tf.keras.__version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "gpu": [tf.config.experimental.get_device_details(g).get("device_name") for g in gpus],
        },
    }
    (OUTPUTS_DIR / "history.json").write_text(json.dumps(history, indent=2) + "\n")
    print(json.dumps(history["training"], indent=2))


if __name__ == "__main__":
    main()
