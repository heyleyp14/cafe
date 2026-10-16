# Capítulo 3: Entrenamiento

Cómo se le enseña a una red neuronal ya entrenada a reconocer hojas de café.

## ¿Por qué existe?

Con unas 3700 fotos (ver el [capítulo 2](02_preparacion_de_datos.md)) no alcanza para enseñarle a una red neuronal a "ver" desde cero: primero tendría que aprender qué es un borde, una textura o una mancha. Sería como enseñarle a leer a alguien que no conoce las letras usando un solo libro.

La solución es el **aprendizaje por transferencia** (*transfer learning*). Imagine contratar a un catador experto en frutas: ya sabe distinguir colores, texturas y manchas. Solo hay que enseñarle el vocabulario del café. En BioCafe ese experto es **EfficientNet-B0**, una red convolucional entrenada previamente con ImageNet (millones de fotos de objetos cotidianos).

## La idea principal

El entrenamiento ocurre en dos etapas, como la formación del catador:

- **Etapa A, la cabeza.** Se congela todo lo que el experto ya sabe (la "base") y solo se entrena una capa nueva al final (la "cabeza") que traduce lo que ve a las cuatro clases. Se usa una tasa de aprendizaje alta (`1e-3`).
- **Etapa B, el ajuste fino.** Se descongela la base y se ajusta todo con una tasa de aprendizaje diez veces menor (`1e-4`), para no borrar lo que ya sabía.

Alrededor de eso hay tres ideas de apoyo: **aumento de datos** (mostrar cada foto girada, con otro brillo o encuadre), **pesos por estrato** (que las fuentes pequeñas no queden opacadas) y **parada temprana** (detenerse cuando la validación deja de mejorar).

## Cómo funciona en este código

Vive en:
- `ml/02_entrenar.py`
- `ml/colab_run_v3.py`
- `ml/config.py`
- `docs/resultados.md`

### El modelo: base congelada + cabeza nueva

```python
base = tf.keras.applications.EfficientNetB0(input_shape=shape, include_top=False, weights="imagenet")
x = inputs
base.trainable = False
x = base(x, training=False)  # BatchNormalization stays in inference mode in both stages
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(x)
```

- `include_top=False` quita la cabeza original de ImageNet (que distinguía mil objetos).
- `GlobalAveragePooling2D` resume lo que vio la base en un vector.
- `Dropout(0.2)` apaga al azar el 20 % de ese vector durante el entrenamiento para que el modelo no memorice.
- `Dense(..., activation="softmax")` produce las cuatro probabilidades que suman 1, tal como exige el [contrato](01_contrato_del_modelo.md).

### Las dos etapas

```python
# Stage A: train the head with the base frozen.
head = fit(model, train_ds, val_ds, 1e-3, epochs_head, patience=4, loss=loss, verbose=verbose)

# Stage B: full fine-tuning. Every base layer is unfrozen except BatchNormalization,
base.trainable = True
for layer in base.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
finetune = fit(model, train_ds, val_ds, 1e-4, epochs_finetune, patience=6, reduce_on_plateau=True, ...)
```

Las capas de `BatchNormalization` se dejan congeladas también en la etapa B: con lotes pequeños sus estadísticas serían inestables, así que se conservan las de ImageNet. `fit` usa `EarlyStopping(monitor="val_loss", restore_best_weights=True)`: si la pérdida de validación no mejora en `patience` épocas, se detiene y recupera los mejores pesos.

La pérdida es entropía cruzada categórica con `label_smoothing=0.1` (`LABEL_SMOOTHING`), que le pide al modelo no estar 100 % seguro de ninguna etiqueta.

### Aumento de datos: la misma hoja, muchas fotos

```python
tf.keras.layers.RandomFlip("horizontal_and_vertical"),
tf.keras.layers.RandomRotation(0.25),
tf.keras.layers.RandomZoom((-0.4, 0.3)),
tf.keras.layers.RandomTranslation(0.15, 0.15),
```

Y en color (`jitter_color`): brillo, contraste, saturación y un cambio de tono muy pequeño (`0.03`), porque, como dice el comentario, "el tono de la lesión (roya naranja, mina café) es parte de la señal". El aumento se aplica solo al conjunto de entrenamiento, nunca a la evaluación, y no se exporta con el modelo.

### Pesos por estrato

```python
def stratum_weights(labels, sources, class_boost=None):
    """Per-sample weights inversely proportional to the size of the (source, class) stratum.
```

Cada foto pesa en la pérdida de forma inversa al tamaño de su estrato `(fuente, clase)`, con un tope de 5 veces el peso más ligero (`MAX_WEIGHT_RATIO`). Así, las 108 fotos de arañita roja de entrenamiento no quedan ahogadas por las 522 de `rocole/sana` (cifras de `docs/resultados.md`). `docs/decisiones.md` registra que esto reemplazó al `class_weight` por clase de la v1.

### Por qué EfficientNet-B0 y no MobileNetV2

El plan original usaba MobileNetV2. `docs/decisiones.md` explica el cambio: entrenando sin BRACOL y midiendo en BRACOL (una fuente que el modelo no había visto), EfficientNet-B0 obtuvo F1 macro 0.8494 frente a 0.7313 de MobileNetV2. Esa comparación, llamada "etapa 1", se detalla en `docs/resultados.md` y en el [capítulo 4](04_evaluacion_umbral_y_duda.md).

### Dónde se entrenó

`docs/decisiones.md` fija que el modelo entregado se entrena en Google Colab o Kaggle con GPU. `ml/colab_run_v3.py` automatiza dos corridas: `stage1_v3` (sin BRACOL, para medir) y `final` (con todas las fuentes):

```python
for name, extra in (("stage1_v3", ["--holdout-source", HOLDOUT]), ("final", [])):
    run("02_entrenar.py", "--run", name, "--arch", ARCH, *extra)
    ...
    assert min(val_loss) < val_loss[0], "validation loss never improved over epoch 1"
```

La aserción es una red de seguridad: si la validación nunca mejoró, algo salió mal y la corrida se detiene.

Según `docs/resultados.md`, el modelo final se entrenó en una Tesla T4 en 1671.0 s, con 10 épocas de cabeza y 22 de ajuste fino (de 40 pedidas, cortadas por la parada temprana), con TensorFlow 2.21.0 y Keras 3.15.1. La pérdida de validación bajó de 0.9312 en la época 1 a un mínimo de 0.5126.

El resultado es `ml/outputs/final/model.keras` y su `labels.txt`.

## Cómo se conecta

- Recibe las particiones de la [preparación de datos](02_preparacion_de_datos.md).
- **Produce el modelo** que examina la [evaluación](04_evaluacion_umbral_y_duda.md).
- **Entrega `model.keras`** a la [conversión a TFLite](05_conversion_y_paridad.md).
- Se lanza desde Colab gracias a la [orquestación](10_orquestacion_y_entrega.md).

## Resumen

El modelo es EfficientNet-B0 preentrenado en ImageNet, con una cabeza nueva de cuatro clases, entrenado en dos etapas (cabeza y ajuste fino), con aumento de datos, pesos por estrato y parada temprana, en una GPU de Colab. Un modelo entrenado todavía no sirve de nada si no sabemos qué tan bien funciona: eso es el siguiente capítulo.

Ver también: [Glosario](glosario.md)
