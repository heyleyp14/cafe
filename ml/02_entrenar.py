"""Phase 2 (model v2): train MobileNetV2 or EfficientNetB0 (head, then full fine-tuning).

Writes outputs/<run>/model.keras, labels.txt and history.json. The model follows the
section 4 contract: float32 RGB 0-255 input, normalization inside, softmax output.
Steps R3 and R4 of docs/PLAN_reentrenamiento_v2.md.
"""
import argparse
import json
import math
import platform
import time
from collections import Counter

import numpy as np
import tensorflow as tf

from config import CLASSES, IMG_SIZE, OUTPUTS_DIR, SEED, list_processed

BATCH_SIZE = 32
ARCHITECTURES = ("mobilenetv2", "efficientnetb0")
LABEL_SMOOTHING = 0.1
MAX_WEIGHT_RATIO = 5.0  # no stratum weighs more than this many times the lightest one


def load_image(path):
    """Decode and squash to 224x224. Must stay identical to 05_paridad_tflite.load_resized."""
    image = tf.io.decode_jpeg(tf.io.read_file(path), channels=3)
    return tf.image.resize(image, (IMG_SIZE, IMG_SIZE), method="bilinear")  # float32 0..255


def jitter_color(image):
    """Per-image colour and lighting changes; values stay in 0..255."""
    image = image / 255.0
    image = tf.image.random_brightness(image, 0.2)
    image = tf.image.random_contrast(image, 0.7, 1.3)
    image = tf.image.random_saturation(image, 0.7, 1.3)
    # Small on purpose: the hue of the lesion (orange rust, brown mine) is part of the signal.
    image = tf.image.random_hue(image, 0.03)
    return tf.clip_by_value(image, 0.0, 1.0) * 255.0


def build_geometry():
    """Geometric augmentation, applied per batch in the data pipeline (never exported).

    R0 found the model sensitive to framing and scale: cropping BRACOL to the leaf
    dropped accuracy and pushed predictions to `minador`, because in training the
    close-ups were mostly minador crops. Every class must be seen at several scales.
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        # Up to +-90 degrees: a leaf has no canonical orientation, and with the flips
        # this covers every angle. The squash resize already distorts the aspect ratio.
        tf.keras.layers.RandomRotation(0.25),
        # Negative zooms in (leaf close-up, up to 40 %), positive zooms out (leaf small in
        # the frame, up to 30 %); height and width are drawn together to keep the shape.
        tf.keras.layers.RandomZoom((-0.4, 0.3)),
        # The leaf is not always centred in a phone picture.
        tf.keras.layers.RandomTranslation(0.15, 0.15),
        # The default fill ("reflect") continues the background instead of adding a black
        # border, which no real picture has.
    ])


def make_dataset(paths, labels, weights=None, augment=None):
    """tf.data pipeline from explicit file lists, so sources can be filtered."""
    one_hot = tf.one_hot(labels, len(CLASSES))
    training = weights is not None
    tensors = (paths, one_hot, np.asarray(weights, np.float32)) if training else (paths, one_hot)
    dataset = tf.data.Dataset.from_tensor_slices(tensors)
    if training:
        dataset = dataset.shuffle(len(paths), seed=SEED, reshuffle_each_iteration=True)
        dataset = dataset.map(lambda path, y, w: (jitter_color(load_image(path)), y, w),
                              num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.batch(BATCH_SIZE)
        dataset = dataset.map(
            lambda x, y, w: (tf.clip_by_value(augment(x, training=True), 0.0, 255.0), y, w),
            num_parallel_calls=tf.data.AUTOTUNE)
    else:
        dataset = dataset.map(lambda path, y: (load_image(path), y), num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.batch(BATCH_SIZE)
    return dataset.prefetch(tf.data.AUTOTUNE)


def stratum_weights(labels, sources):
    """Per-sample weights inversely proportional to the size of the (source, class) stratum.

    Replaces class_weight: a class is no longer learnt mostly from its biggest source.
    Weights are capped at MAX_WEIGHT_RATIO times the smallest and normalized to mean 1.
    """
    keys = [f"{source}/{CLASSES[label]}" for source, label in zip(sources, labels)]
    counts = Counter(keys)
    lightest = 1 / max(counts.values())
    raw = {key: min(1 / n, MAX_WEIGHT_RATIO * lightest) for key, n in counts.items()}
    mean = sum(raw[key] for key in keys) / len(keys)
    weights = {key: value / mean for key, value in raw.items()}
    return [weights[key] for key in keys], dict(sorted(counts.items())), dict(sorted(weights.items()))


def build_model(arch):
    shape = (IMG_SIZE, IMG_SIZE, 3)
    inputs = tf.keras.Input(shape)  # float32 0..255
    if arch == "mobilenetv2":
        base = tf.keras.applications.MobileNetV2(input_shape=shape, include_top=False, weights="imagenet")
        x = tf.keras.layers.Rescaling(1 / 127.5, offset=-1)(inputs)  # normalization INSIDE the model
    else:
        # EfficientNetB0 carries its own Rescaling and Normalization layers and expects
        # 0..255, so the normalization is already inside the model.
        base = tf.keras.applications.EfficientNetB0(input_shape=shape, include_top=False, weights="imagenet")
        x = inputs
    base.trainable = False
    x = base(x, training=False)  # BatchNormalization stays in inference mode in both stages
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(x)
    return tf.keras.Model(inputs, outputs), base


def fit(model, train_ds, val_ds, learning_rate, epochs, patience, reduce_on_plateau=False):
    # Compiling here also applies the `trainable` changes made before the stage.
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate),
                  loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
                  metrics=["accuracy"])
    callbacks = [tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=patience,
                                                  restore_best_weights=True)]
    if reduce_on_plateau:
        callbacks.append(tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2,
                                                              min_lr=1e-6))
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=callbacks).history
    return {name: [float(value) for value in values] for name, values in history.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", choices=ARCHITECTURES, default="mobilenetv2")
    parser.add_argument("--run", default="default", help="outputs go to outputs/<run>/")
    parser.add_argument("--holdout-source", default=None,
                        help="source left out of training and validation (evaluated by 03_evaluar.py)")
    parser.add_argument("--epochs-head", type=int, default=10)
    parser.add_argument("--epochs-finetune", type=int, default=40)
    args = parser.parse_args()

    tf.keras.utils.set_random_seed(SEED)
    train_paths, train_labels, train_sources = list_processed(["train"], exclude_source=args.holdout_source)
    val_paths, val_labels, _ = list_processed(["val"], exclude_source=args.holdout_source)
    if not train_paths or not val_paths:
        raise SystemExit("No training or validation images: run 01_preparar_datos.py first")
    missing = [label for index, label in enumerate(CLASSES) if index not in set(train_labels)]
    if missing:
        raise SystemExit(f"Classes without training images: {missing}")

    weights, stratum_counts, weight_by_stratum = stratum_weights(train_labels, train_sources)
    train_ds = make_dataset(train_paths, train_labels, weights, build_geometry())
    val_ds = make_dataset(val_paths, val_labels)

    model, base = build_model(args.arch)
    started = time.time()

    # Stage A: train the head with the base frozen.
    head = fit(model, train_ds, val_ds, 1e-3, args.epochs_head, patience=4)

    # Stage B: full fine-tuning. Every base layer is unfrozen except BatchNormalization,
    # whose statistics and weights stay as in ImageNet.
    base.trainable = True
    for layer in base.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
    finetune = fit(model, train_ds, val_ds, 1e-4, args.epochs_finetune, patience=6, reduce_on_plateau=True)

    seconds = time.time() - started
    run_dir = OUTPUTS_DIR / args.run
    run_dir.mkdir(parents=True, exist_ok=True)
    model.save(run_dir / "model.keras")
    (run_dir / "labels.txt").write_text("\n".join(CLASSES) + "\n")

    gpus = tf.config.list_physical_devices("GPU")
    history = {
        "head": head,
        "finetune": finetune,
        "sample_weights": {
            "rule": f"1 / stratum size, capped at {MAX_WEIGHT_RATIO}x the smallest, mean 1",
            "stratum_counts": stratum_counts,
            "stratum_weights": {key: round(value, 4) for key, value in weight_by_stratum.items()},
        },
        "training": {
            "arch": args.arch,
            "run": args.run,
            "holdout_source": args.holdout_source,
            "images": {"train": len(train_paths), "val": len(val_paths)},
            "steps_per_epoch": math.ceil(len(train_paths) / BATCH_SIZE),
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
    (run_dir / "history.json").write_text(json.dumps(history, indent=2) + "\n")
    print(json.dumps({**history["training"], "sample_weights": history["sample_weights"]}, indent=2))


if __name__ == "__main__":
    main()
