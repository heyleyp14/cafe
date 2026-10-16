# Capítulo 5: Conversión a TFLite y paridad

Cómo el modelo de Keras se convierte en un archivo que el teléfono puede ejecutar, y cómo se comprueba que responda igual.

## ¿Por qué existe?

`model.keras` es un modelo pensado para un computador con Python y TensorFlow completos. Un teléfono Android no tiene ninguno de los dos. Hay que **traducirlo** a TensorFlow Lite (TFLite), un formato compacto que ejecuta el intérprete de LiteRT dentro de la app.

Toda traducción puede cambiar el sentido. Imagine traducir un libro y luego pedirle a alguien que compare cada frase con el original: eso es la **paridad**. Sin ella, un error en la conversión, o en cómo la app prepara la imagen, pasaría desapercibido: la app seguiría mostrando resultados, pero distintos de los que se midieron en el [capítulo 4](04_evaluacion_umbral_y_duda.md).

## La idea principal

1. **Convertir** el modelo a dos versiones TFLite: una sin cuantizar (`float32`, "fp32") y otra con cuantización de rango dinámico (pesos en 8 bits, más pequeña).
2. **Comparar** las tres versiones (Keras, fp32, cuantizada) con las mismas imágenes.
3. **Exportar imágenes de referencia** ("golden") con las probabilidades exactas que el teléfono debe reproducir.
4. **Probar en el teléfono** en dos niveles, como pide el [contrato](01_contrato_del_modelo.md):
   - **Nivel 1**: el modelo aislado, con exactamente los mismos números de entrada que usó Python.
   - **Nivel 2**: el flujo completo (decodificar el JPEG y escalarlo en Android), donde se tolera una pequeña diferencia de probabilidades pero no de clase.

## Cómo funciona en este código

Vive en:
- `ml/04_convertir_tflite.py`
- `ml/05_paridad_tflite.py`
- `ml/outputs/final/model_io.json` y `ml/outputs/final/parity.json`
- `android/app/src/androidTest/assets/golden/golden.json`
- `android/app/src/androidTest/java/co/edu/unipamplona/cafedetector/ml/CoffeeLeafClassifierTest.kt`
- `docs/decisiones.md`

### La conversión

```python
# fp32 reference
(OUTPUTS_DIR / "model_fp32.tflite").write_bytes(
    tf.lite.TFLiteConverter.from_keras_model(model).convert())

# dynamic-range quantization: int8 weights, input/output stay float32
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
(OUTPUTS_DIR / "model.tflite").write_bytes(converter.convert())
```

Según `ml/outputs/final/model_io.json`, `model_fp32.tflite` pesa 16 077 592 bytes y `model.tflite` (cuantizado) 4 573 960 bytes. Ambos cumplen el contrato: entrada `[1, 224, 224, 3]` y salida `[1, 4]`, las dos `float32`.

### Comparar las tres versiones

`05_paridad_tflite.py` toma 100 imágenes de prueba al azar (semilla fija), las pasa por los tres modelos y calcula, para cada par, en qué fracción coincide la clase y cuál es la mayor diferencia de probabilidad:

```python
def compare(reference, candidate):
    return {
        "argmax_agreement": round(float((reference.argmax(1) == candidate.argmax(1)).mean()), 4),
        "max_abs_probability_difference": round(float(np.abs(reference - candidate).max()), 6),
    }
```

`ml/outputs/final/parity.json` muestra que las tres versiones coinciden en la clase en las 100 imágenes, pero la diferencia máxima de probabilidad es muy distinta: 0.000443 entre Keras y fp32, y 0.157247 entre Keras y la cuantizada.

### Por qué la app lleva el modelo fp32

Esta es una de las decisiones clave del proyecto (`docs/decisiones.md`, "Modelo que se entrega en la app: fp32"). El plan pedía a la vez cuantizar el modelo y que la diferencia de probabilidad entre Android y Python fuera menor que 0.01. Con el modelo cuantizado, esa prueba falló en 2 de 10 imágenes cuando se tomó la decisión, porque sus resultados dependen de la CPU. Se eligió la opción más exacta a cambio de un archivo más grande. La constante que lo fija está en `ml/config.py`:

```python
# Model shipped in the app as assets/model.tflite. The float32 file is used because the
# dynamic-range one gives CPU-dependent probabilities (docs/decisiones.md, phase 8).
APP_MODEL_FILE = "model_fp32.tflite"
```

### Las imágenes de referencia (golden)

`export_golden` elige 10 imágenes de prueba (2 de arañita roja, 2 de minador, 3 de roya y 3 de sana) y guarda tres cosas por cada una:

```python
shutil.copyfile(path, golden_dir / f"{name}.jpg")
rgb = np.clip(np.rint(load_resized(path)), 0, 255).astype(np.uint8)
(golden_dir / f"{name}.rgb").write_bytes(rgb.tobytes())  # 224*224*3 raw RGB bytes
# Probabilities come from the .rgb bytes: exactly what Android will feed the model.
probabilities = app_model(rgb.astype(np.float32))
```

- `NN.jpg`: la foto original, para el nivel 2.
- `NN.rgb`: los 224×224×3 bytes ya redimensionados por Python, para el nivel 1.
- `golden.json`: las probabilidades que da el modelo de la app con esos bytes.

Fíjese en que las probabilidades se calculan sobre los bytes **redondeados** a enteros, no sobre los flotantes originales: es exactamente lo que Android leerá. Según `parity.json`, en 8 de las 10 imágenes golden la clase predicha coincide con la etiqueta real; eso no es un fallo de paridad, sino un reflejo de la exactitud del modelo.

### Las pruebas en el teléfono

`CoffeeLeafClassifierTest.kt` es una prueba instrumentada (se ejecuta en un teléfono o emulador):

```kotlin
/** Level 1: the model alone, fed the exact bytes Python used. */
@Test
fun rgbBytesGiveTheSameProbabilitiesAsPython() {
    ...
    assertTrue("max probability difference is ${worst.value} in ${worst.key}; all: $maxDifferences", worst.value < 0.01f)
}

/** Level 2: full flow (decode + scale on Android). Probabilities may differ, the class should not. */
@Test
fun jpegFlowGivesTheSameClassInAtLeastNineOfTen() {
```

`docs/decisiones.md` aclara que en el nivel 2 la clase de Android se compara con la que predice TFLite en Python, no con la etiqueta real: es una prueba de fidelidad, no de exactitud.

Resultados en un teléfono real (motorola edge 30, Android 14), según `docs/resultados.md`: diferencia máxima de probabilidad de 0.0000006 en el nivel 1 (límite 0.01) y 10 de 10 clases coincidentes en el nivel 2.

## Cómo se conecta

- Recibe `model.keras` del [entrenamiento](03_entrenamiento.md).
- Es donde **se verifica** el [contrato del modelo](01_contrato_del_modelo.md).
- **Entrega `model.tflite`** (la versión fp32 renombrada) al [clasificador en el teléfono](06_clasificador_en_el_telefono.md).

## Resumen

La conversión produce dos modelos TFLite; la paridad demuestra que el fp32 responde casi idéntico a Keras y que el teléfono reproduce esas respuestas, en el modelo aislado y en el flujo completo. Por eso la app lleva el fp32. En el próximo capítulo entramos al código Kotlin que ejecuta ese modelo.

Ver también: [Glosario](glosario.md)
