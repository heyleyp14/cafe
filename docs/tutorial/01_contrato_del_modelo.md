# Capítulo 1: El contrato del modelo

El acuerdo que hace que el modelo entrenado en Python funcione igual dentro de la app en Kotlin.

## ¿Por qué existe?

Imagine dos carpinteros en talleres distintos. Uno fabrica una puerta; el otro, el marco. Si no comparten el mismo plano (alto, ancho, dónde van las bisagras), la puerta no entra aunque ambos hayan hecho un trabajo impecable.

En BioCafe pasa lo mismo. El modelo se entrena en Python ([capítulo 3](03_entrenamiento.md)) y se ejecuta en un teléfono con Kotlin ([capítulo 6](06_clasificador_en_el_telefono.md)). Si Python le muestra al modelo fotos de un tamaño, con un orden de colores o con valores en un rango, y la app le entrega algo distinto, el modelo responde cualquier cosa sin dar error. El plan del proyecto lo advierte de forma directa:

> La mayoría de fallos en estos proyectos vienen de un preprocesamiento distinto entre entrenamiento y app.
> — `PLAN_Prototipo_Cafe_Kotlin.md`, sección 4

Por eso el proyecto empieza fijando un **contrato**: una tabla de reglas que ambos lados deben respetar.

## La idea principal

El contrato responde cinco preguntas:

1. **¿Qué entra?** Un tensor `float32` con forma `[1, 224, 224, 3]`: una imagen de 224×224 píxeles, tres canales en orden **RGB**, con valores de **0 a 255** (sin normalizar).
2. **¿Quién normaliza?** El propio modelo. La app **no** normaliza.
3. **¿Cómo se redimensiona?** "Squash": la foto completa se aplasta a 224×224, sin recortar y sin conservar la proporción. Igual en entrenamiento y en la app.
4. **¿Qué sale?** Un tensor `float32 [1, N]` de probabilidades (softmax), donde N es el número de clases.
5. **¿Qué significa cada posición de la salida?** El orden de `labels.txt`: la línea 0 es la clase 0, y así sucesivamente.

Además, la imagen debe llegar "derecha" (con la rotación EXIF o de la cámara ya aplicada), y el archivo `threshold.json` lleva la versión del modelo que la app muestra en "Acerca de".

La regla 2 es la más interesante: al meter la normalización *dentro* del modelo, se elimina toda una familia de errores. La app solo tiene que entregar píxeles crudos; no puede equivocarse con una media o una desviación mal copiada.

## Cómo funciona en este código

Vive en:
- `PLAN_Prototipo_Cafe_Kotlin.md` (sección 4, la tabla del contrato)
- `ml/config.py`
- `android/app/src/main/assets/labels.txt`
- `android/app/src/main/assets/threshold.json`
- `ml/04_convertir_tflite.py` y `ml/outputs/final/model_io.json`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ml/CoffeeLeafClassifier.kt`

### El orden de las clases, fijado una sola vez

En `ml/config.py`:

```python
# Alphabetical and fixed: this is the order of labels.txt (contract, section 4).
CLASSES = ["arana_roja", "minador", "roya", "sana"]
IMG_SIZE = 224
SEED = 42
```

`CLASSES` es la fuente de verdad. El script de entrenamiento escribe `labels.txt` a partir de esta lista, y ese mismo archivo se copia a `android/app/src/main/assets/labels.txt`, que contiene exactamente:

```text
arana_roja
minador
roya
sana
```

Si alguien reordenara la lista en un lado y no en el otro, la app diría "roya" cuando el modelo quiso decir "minador". Por eso el orden es alfabético y "fijo".

### La normalización va dentro del modelo

En `ml/02_entrenar.py`, la función `build_model` construye el modelo así:

```python
inputs = tf.keras.Input(shape)  # float32 0..255
if arch == "mobilenetv2":
    ...
    x = tf.keras.layers.Rescaling(1 / 127.5, offset=-1)(inputs)  # normalization INSIDE the model
else:
    # EfficientNetB0 carries its own Rescaling and Normalization layers and expects
    # 0..255, so the normalization is already inside the model.
    ...
    x = inputs
```

El plan proponía una capa `Rescaling(1/127.5, offset=-1)`, que es lo que necesita MobileNetV2. El modelo final es EfficientNet-B0, que ya trae sus propias capas de reescalado y normalización y espera valores 0–255. En los dos casos se cumple la regla: la normalización vive dentro del modelo.

### El "squash" a 224×224

En Python (`ml/02_entrenar.py`):

```python
def squash(image, img_size=IMG_SIZE):
    """Whole image to img_size x img_size, no crop and no aspect preservation (as the app does)."""
    return tf.image.resize(image, (img_size, img_size), method="bilinear")  # float32 0..255
```

Y en Kotlin (`CoffeeLeafClassifier.kt`):

```kotlin
val scaled = Bitmap.createScaledBitmap(bitmap, SIZE, SIZE, true) // squash
scaled.getPixels(pixels, 0, SIZE, 0, 0, SIZE, SIZE)
...
for (p in pixels) { // RGB, 0..255, not normalized
    input.putFloat(((p shr 16) and 0xFF).toFloat())
    input.putFloat(((p shr 8) and 0xFF).toFloat())
    input.putFloat((p and 0xFF).toFloat())
}
```

Las dos versiones hacen lo mismo con herramientas distintas: aplastan la foto entera a 224×224 y dejan los valores en 0–255. En Kotlin, cada píxel viene empaquetado como un entero ARGB; los desplazamientos `shr 16`, `shr 8` y la máscara `and 0xFF` extraen el rojo, el verde y el azul, en ese orden (RGB).

### Se comprueba automáticamente

El contrato no queda solo en el papel. Después de convertir el modelo, `ml/04_convertir_tflite.py` verifica la forma y el tipo de la entrada y la salida:

```python
assert description["inputs"][0]["shape"] == [1, IMG_SIZE, IMG_SIZE, 3], description
assert description["inputs"][0]["dtype"] == "float32", description
assert description["outputs"][0]["shape"] == [1, len(CLASSES)], description
```

Si todo pasa, escribe `"contract_ok": true` en `ml/outputs/final/model_io.json`, donde se lee que ambos modelos convertidos tienen entrada `[1, 224, 224, 3]` `float32` y salida `[1, 4]` `float32`.

En el teléfono hay una segunda barrera: `CoffeeLeafClassifier` se niega a arrancar si el modelo y `labels.txt` no tienen el mismo número de clases:

```kotlin
check(outputCount == labels.size) {
    "Model outputs $outputCount classes but $LABELS_ASSET has ${labels.size}"
}
```

### Una diferencia conocida y aceptada

El plan reconoce que TensorFlow y Android escalan y decodifican JPEG con algoritmos ligeramente distintos, así que las probabilidades de una misma foto pueden variar un poco. Por eso la fidelidad se prueba en **dos niveles**: primero el modelo aislado con exactamente los mismos números de entrada, y después el flujo completo con una tolerancia razonable. Ese tema se desarrolla en el [capítulo 5](05_conversion_y_paridad.md).

## Cómo se conecta

- El contrato **fija el formato** que debe producir la [preparación de datos](02_preparacion_de_datos.md) y que consume el [entrenamiento](03_entrenamiento.md).
- **Se verifica** en la [conversión a TFLite y paridad](05_conversion_y_paridad.md).
- **Dicta el preprocesamiento** del [clasificador en el teléfono](06_clasificador_en_el_telefono.md).

## Resumen

El contrato es el plano compartido entre Python y Kotlin: entrada `float32 [1, 224, 224, 3]` RGB 0–255, normalización dentro del modelo, redimensionado "squash", salida softmax y orden de clases según `labels.txt`. Varias comprobaciones automáticas impiden que se rompa en silencio. En el próximo capítulo veremos de dónde salen las fotos con que se entrena el modelo.

Ver también: [Glosario](glosario.md)
