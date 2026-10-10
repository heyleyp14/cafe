# Plan de implementación: prototipo móvil de detección de plagas y enfermedades en hojas de café

Documento para un agente de IA (o desarrollador) que implemente el prototipo de principio a fin.
Basado en el proyecto "Sistema de Detección Temprana de Plagas y Enfermedades en Cultivos de Café" (FCPD 2026-2, Universidad de Pamplona).
Versión 2 (refinada).

---

## 0. Reglas de trabajo para el agente

1. Ejecuta las fases **en orden**. No avances si no se cumplen los **criterios de aceptación** de la fase actual.
2. Donde diga **DECISIÓN**, usa el valor por defecto salvo instrucción contraria y regístralo en `docs/decisiones.md` (fecha, decisión, motivo).
3. **Nunca inventes resultados.** Todo número (precisión, latencia, tamaño) debe salir de un archivo generado por los scripts o de una prueba ejecutada. Si no pudiste ejecutar algo (no hay GPU, no hay dispositivo, no hay red), escribe "NO EJECUTADO" y por qué.
4. Si falta un dataset, un permiso de red o una herramienta, **detente y pide al humano** lo que necesitas. No sustituyas por datos sintéticos sin avisar.
5. **Verifica versiones de librerías en su fuente** (Maven Central, PyPI) antes de fijarlas; los números de versión de este documento son orientativos.
6. Al cerrar cada fase, escribe en `docs/bitacora.md` qué hiciste, qué comprobaste y qué quedó pendiente.
7. Es un **prototipo académico de apoyo**, no una herramienta de diagnóstico. La app debe decirlo en pantalla.

### Lo que NO debes hacer
- No normalizar la imagen en la app (la normalización va dentro del modelo).
- No evaluar con imágenes que se usaron para entrenar o elegir hiperparámetros.
- No subir datasets ni claves a git.
- No agregar permiso `INTERNET` a la app.
- No dar recomendaciones de manejo (fungicidas, dosis) que no estén en el informe.

---

## 1. Alcance

### 1.1 Qué hace la app
1. El usuario toma una foto de una **hoja** de café o la elige de la galería.
2. Un modelo de clasificación corre **en el teléfono, sin internet** (LiteRT / TensorFlow Lite).
3. La app muestra la clase más probable, la confianza, el top-3 y una ficha informativa.
4. Si la confianza es baja, muestra "No se pudo determinar con seguridad".

### 1.2 Clases según el análisis de viabilidad del informe
| Afectación | ¿Entra? |
|---|---|
| Roya | Sí |
| Minador de la hoja | Sí |
| Arañita roja | Sí (requiere datos propios) |
| Mancha de hierro | Sí (requiere datos propios) |
| Ojo de gallo | Sí (requiere datos propios) |
| Chamusquina | Condicional (solo manifestaciones foliares) |
| Broca | Descartada (se ve en el fruto) |
| Cochinilla de raíces | Descartada (se ve en la raíz) |
| Antracnosis | No priorizada (principalmente frutos) |

Más la clase `sana`.

### 1.3 DECISIÓN: alcance de la v1
- **v1:** `sana`, `roya`, `minador`. Es lo que los datasets citados permiten sin recolectar datos nuevos: **RoCoLe** (1560 imágenes de hojas Robusta, con estado y severidad) y **DECAFIA** (2786 imágenes, 15181 instancias anotadas: roya, "coco", minador y hojas).
- **v2 (fuera de este plan salvo que el humano aporte imágenes):** arañita roja, mancha de hierro, ojo de gallo, chamusquina.
- Verifica qué significa "coco" en DECAFIA antes de mapearlo; no lo asumas.
- **v1.1 opcional:** clase `no_hoja` (manos, suelo, objetos, fondos) para que la app rechace fotos que no son hojas. Solo si el humano aporta o aprueba esas imágenes.

### 1.4 Fuera de alcance
Mask R-CNN y segmentación (demasiado pesado para el teléfono; trabajo futuro en servidor), historial de análisis, cuentas de usuario, backend, iOS.

---

## 2. Stack

| Parte | Tecnología |
|---|---|
| Entrenamiento | Python 3.10+, TensorFlow ≥ 2.16 (Keras 3), NumPy, scikit-learn, matplotlib, Pillow |
| Entorno | Google Colab o Kaggle con GPU (CUDA), como indica el informe; también corre en CPU, más lento |
| Modelo base | MobileNetV2 preentrenado en ImageNet |
| Comparación (opcional) | EfficientNet-B0 y ResNet50 para la tabla del informe |
| Conversión | `tf.lite.TFLiteConverter` |
| App | Kotlin, Android Studio, `minSdk 26`, Jetpack Compose + Material 3 |
| Cámara | CameraX |
| Inferencia | LiteRT (`com.google.ai.edge.litert:litert`) o la clásica `org.tensorflow:tensorflow-lite`. Los **imports cambian según la librería** (`com.google.ai.edge.litert.Interpreter` vs `org.tensorflow.lite.Interpreter`); elige una y úsala en todo el proyecto |
| Arquitectura | MVVM, una Activity, un módulo `app` |

Requisitos de herramientas (fase 0): Python, `pip`, JDK 17, Android SDK (Android Studio o `sdkmanager`), `adb` si se prueba en dispositivo.

---

## 3. Estructura del repositorio

```
cafe-detector/
├── README.md
├── Makefile                      # atajos: make data train eval tflite parity
├── docs/
│   ├── decisiones.md
│   ├── bitacora.md
│   └── resultados.md             # se genera desde ml/outputs/*.json
├── ml/
│   ├── requirements.txt          # versiones fijadas
│   ├── config.py                 # CLASSES, IMG_SIZE=224, SEED=42, rutas
│   ├── 01_preparar_datos.py
│   ├── 02_entrenar.py
│   ├── 03_evaluar.py
│   ├── 04_convertir_tflite.py
│   ├── 05_paridad_tflite.py
│   ├── data/                     # NO va a git
│   │   ├── raw/
│   │   └── processed/{train,val,test}/<clase>/*.jpg
│   └── outputs/                  # model.keras, model.tflite, labels.txt,
│                                 # threshold.json, metrics.json, parity.json,
│                                 # confusion_matrix.png, golden/
└── android/
    └── app/src/
        ├── main/
        │   ├── assets/           # model.tflite, labels.txt, threshold.json, conditions.json
        │   ├── res/values/strings.xml    # TODOS los textos en español aquí
        │   └── java/.../
        │       ├── MainActivity.kt
        │       ├── ml/CoffeeLeafClassifier.kt
        │       ├── ml/ImageUtils.kt
        │       ├── data/ConditionsRepository.kt
        │       ├── ui/{HomeScreen,CameraScreen,ResultScreen}.kt
        │       └── ui/ClassifierViewModel.kt
        ├── test/                 # unitarias
        └── androidTest/          # paridad + latencia (assets/golden/)
```

`.gitignore`: `ml/data/`, `*.keras`, `build/`, `.gradle/`, `local.properties`. El `.tflite`, `labels.txt` y `threshold.json` **sí** se versionan.

---

## 4. CONTRATO ENTRE EL MODELO Y LA APP

La mayoría de fallos en estos proyectos vienen de un preprocesamiento distinto entre entrenamiento y app. Se fija así:

| Elemento | Valor |
|---|---|
| Entrada | `float32`, forma `[1, 224, 224, 3]`, orden **RGB**, valores **0–255** |
| Normalización | dentro del modelo (`Rescaling(1/127.5, offset=-1)`); la app NO normaliza |
| Redimensionado | "squash" a 224×224 (sin recorte ni conservar proporción), en entrenamiento y en la app |
| Salida | `float32 [1, N]`, probabilidades (softmax) |
| Clases | orden de `labels.txt`, una por línea, índice = línea |
| Orientación | la imagen llega a la app ya en posición vertical (EXIF / `rotationDegrees`) |
| Versión | `model_version` en `threshold.json` (ej. `"v1-2026-10"`); la app la muestra en "Acerca de" |

**Diferencia conocida de remuestreo:** TensorFlow y Android escalan con algoritmos ligeramente distintos y el JPEG se decodifica con librerías distintas, así que las probabilidades de una misma foto pueden variar un poco. Por eso la paridad se prueba en **dos niveles** (fases 5 y 11): primero el modelo aislado con tensores idénticos, luego el flujo completo con tolerancia razonable.

---

## FASE 0. Preparación del entorno

1. Crear la estructura de la sección 3, `git init`, `.gitignore`.
2. `ml/requirements.txt` con versiones fijadas tras comprobar que instalan y que la conversión TFLite funciona.
3. `ml/config.py`:
   ```python
   CLASSES = ["minador", "roya", "sana"]   # orden alfabético, fijo; es el orden de labels.txt
   IMG_SIZE = 224
   SEED = 42
   ```
4. Comprobar herramientas: `python --version`, `java -version`, Android SDK, GPU (`nvidia-smi` o Colab). Anotar lo que falte en la bitácora.
5. **Licencias:** anotar en `docs/decisiones.md` la licencia/condiciones de uso de RoCoLe y DECAFIA y citarlos en el README. No redistribuir imágenes en el repositorio.

**Aceptación:** estructura creada, entorno comprobado, licencias anotadas.

---

## FASE 1. Datos (`ml/01_preparar_datos.py`)

**Salida:** `ml/data/processed/{train,val,test}/<clase>/` con etiquetas a nivel de imagen y `outputs/dataset_stats.json`.

1. Obtener RoCoLe y DECAFIA (fuentes en las referencias del informe). Sin red: pedir los archivos al humano.
2. Leer anotaciones y construir una tabla `imagen → clase`.
3. **DECISIÓN (imágenes con varias clases):** en DECAFIA una imagen puede tener roya y minador. Por defecto, etiqueta = **clase dominante** (más instancias). Si hay empate o ninguna clase de la v1, se descarta. Registrar cuántas se descartaron.
4. Mapear a `CLASSES`. Revisar a mano una muestra de ~20 imágenes por clase (abrir y mirar) para detectar etiquetas absurdas.
5. **Dividir 70/15/15 estratificado por imagen original, con semilla fija, antes de cualquier aumento.** Si hay fotos de la misma planta o lote (revisar nombres/metadatos), mantenerlas juntas en una sola partición.
6. Detectar duplicados por hash perceptual o MD5 y eliminarlos.
7. Generar `dataset_stats.json` con conteos por clase y partición, y los descartes.

**Aceptación:**
- Ninguna imagen (por hash) está en dos particiones.
- Cada clase tiene al menos ~100 imágenes de entrenamiento; si no, avisar al humano.
- El desbalance (razón clase mayor / menor) está reportado.

---

## FASE 2. Entrenamiento (`ml/02_entrenar.py`)

```python
import tensorflow as tf
from config import CLASSES, IMG_SIZE, SEED

tf.keras.utils.set_random_seed(SEED)

def load(split, shuffle):
    return tf.keras.utils.image_dataset_from_directory(
        f"data/processed/{split}", image_size=(IMG_SIZE, IMG_SIZE),   # squash por defecto
        label_mode="categorical", batch_size=32, shuffle=shuffle,
        seed=SEED, class_names=CLASSES)

train_ds, val_ds = load("train", True), load("val", False)

# Aumento solo en la tubería de datos; NO forma parte del modelo exportado
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

base = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet")
base.trainable = False

inputs = tf.keras.Input((IMG_SIZE, IMG_SIZE, 3))                 # float32 0..255
x = tf.keras.layers.Rescaling(1/127.5, offset=-1)(inputs)        # normalización DENTRO del modelo
x = base(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(x)
model = tf.keras.Model(inputs, outputs)
```

Pasos:
1. **Etapa A (cabeza):** `Adam(1e-3)`, `categorical_crossentropy`, hasta ~15 épocas, `EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True)`.
2. **Etapa B (ajuste fino):** descongelar las últimas ~30 capas de `base`, **dejando todas las `BatchNormalization` congeladas** (`layer.trainable = False`), `Adam(1e-5)`, hasta ~10 épocas, recompilar antes de entrenar.
3. Si hay desbalance, usar `class_weight` calculado desde `dataset_stats.json`.
4. Guardar `outputs/model.keras`, `outputs/labels.txt` (orden de `CLASSES`), `outputs/history.json`.
5. Fijar versiones y semilla; anotar en la bitácora el hardware usado y el tiempo de entrenamiento.

**Aceptación:** se generan los tres archivos; la pérdida de validación baja respecto a la época 1; las curvas no muestran sobreajuste extremo (si lo hay, aumentar regularización o datos y reportar).

---

## FASE 3. Evaluación y umbral (`ml/03_evaluar.py`)

Sobre **test** (no usado para decidir nada):
- exactitud, precisión, recall y F1 por clase, y **F1 macro** (la métrica principal si hay desbalance),
- matriz de confusión → `confusion_matrix.png`,
- todo en `outputs/metrics.json`.

**DECISIÓN – umbral de confianza:**
1. Con las probabilidades de **validación** (no test), calcular para umbrales de 0.40 a 0.95 la fracción de imágenes aceptadas y la exactitud sobre las aceptadas.
2. Elegir el menor umbral con exactitud aceptada ≥ 0.90 (por defecto 0.60 si no se alcanza). Guardar `outputs/threshold.json`: `{"threshold": 0.60, "model_version": "..."}`.
3. Reportar en test el mismo cálculo (cobertura vs. exactitud) con el umbral elegido.

**Aviso para el informe:** softmax tiende a ser sobreconfiado y un modelo entrenado solo con hojas nunca ve "otras cosas". El umbral mitiga pero no resuelve fotos que no son hojas; por eso existe la clase opcional `no_hoja` (v1.1).

Opcional: repetir fases 2–3 con EfficientNet-B0 y ResNet50 (cada una con su propio preprocesado dentro del modelo) y generar una tabla comparativa en `outputs/comparacion.json` con F1 macro, tamaño del `.tflite` y latencia.

**Aceptación:** `metrics.json`, `confusion_matrix.png` y `threshold.json` generados. Si el recall de alguna clase es bajo, repórtalo, no lo ocultes.

---

## FASE 4. Conversión (`ml/04_convertir_tflite.py`)

```python
import tensorflow as tf
model = tf.keras.models.load_model("outputs/model.keras")

# fp32 de referencia
open("outputs/model_fp32.tflite", "wb").write(
    tf.lite.TFLiteConverter.from_keras_model(model).convert())

# cuantización de rango dinámico: pesos int8, E/S siguen en float32
conv = tf.lite.TFLiteConverter.from_keras_model(model)
conv.optimizations = [tf.lite.Optimize.DEFAULT]
open("outputs/model.tflite", "wb").write(conv.convert())
```

- Usa rango dinámico a propósito: tamaño ~4× menor y entrada/salida `float32`, lo que simplifica la app.
- Inspeccionar con `tf.lite.Interpreter(...).get_input_details()/get_output_details()` y confirmar el contrato de la sección 4. Guardar el resultado en `outputs/model_io.json`.

**Aceptación:** `model.tflite` existe, entrada `[1,224,224,3] float32`, salida `[1,N] float32`, N = `len(CLASSES)`.

---

## FASE 5. Paridad y vectores de referencia (`ml/05_paridad_tflite.py`)

**Nivel 1 – Keras vs TFLite (PC):** con 100 imágenes de test, comparar `argmax` y diferencia máxima de probabilidad entre `model.keras`, `model_fp32.tflite` y `model.tflite`. Guardar en `parity.json`. Esperado: ≥ 98 % de coincidencia de clase para el cuantizado.

**Nivel 2 – vectores para Android:** exportar 10 imágenes de test (≥ 2 por clase) a `outputs/golden/`:
- `NN.jpg`: la imagen original,
- `NN.rgb`: **bytes crudos** de la imagen ya redimensionada a 224×224 RGB (224·224·3 bytes, uint8),
- `golden.json`: `[{file, expected_class, probs_tflite}]`, con `probs_tflite` calculadas por el intérprete TFLite en Python **a partir del `.rgb`**.

Medir también latencia en PC (solo referencia).

**Aceptación:** `parity.json` y `golden/` generados. Copiar: `model.tflite`, `labels.txt`, `threshold.json` → `android/app/src/main/assets/`; `golden/` → `android/app/src/androidTest/assets/golden/`.

---

## FASE 6. Proyecto Android: base

1. Crear proyecto Compose (paquete `co.edu.unipamplona.cafedetector`, ajustable), `minSdk 26`.
2. Usar `gradle/libs.versions.toml`. Dependencias (versiones a verificar):
   ```kotlin
   implementation("androidx.camera:camera-core:<ver>")
   implementation("androidx.camera:camera-camera2:<ver>")
   implementation("androidx.camera:camera-lifecycle:<ver>")
   implementation("androidx.camera:camera-view:<ver>")
   implementation("com.google.ai.edge.litert:litert:<ver>")          // o org.tensorflow:tensorflow-lite
   implementation("com.google.ai.edge.litert:litert-support:<ver>")  // solo si usas FileUtil
   implementation("androidx.lifecycle:lifecycle-viewmodel-compose:<ver>")
   implementation("androidx.navigation:navigation-compose:<ver>")
   implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:<ver>")
   ```
3. No comprimir el modelo: `android { androidResources { noCompress += "tflite" } }`.
4. `AndroidManifest.xml`: permiso `CAMERA` y `<uses-feature android:name="android.hardware.camera" android:required="false"/>`. Sin `INTERNET`.
5. Copiar a `assets/` los archivos de la fase 5 y `conditions.json` (fase 7).

**Aceptación:** `./gradlew assembleDebug` compila y la app abre sin fallar.

---

## FASE 7. Contenido informativo (`assets/conditions.json`)

Una entrada por clase, con textos en español **tomados del informe** (secciones 1.1 y 1.2: descripción, características visuales, condiciones favorables). Sin recomendaciones de manejo que no estén en el informe.

```json
{
  "roya":    { "nombre": "Roya del café", "sintomas": "…del informe…", "condiciones": "…del informe…" },
  "minador": { "nombre": "Minador de las hojas del cafeto", "sintomas": "…", "condiciones": "…" },
  "sana":    { "nombre": "Hoja sana", "sintomas": "No se observan signos de plagas o enfermedades.", "condiciones": "" }
}
```

`ConditionsRepository` lo carga con `kotlinx.serialization`. Los textos de interfaz van en `strings.xml`.

**Aceptación:** cada línea de `labels.txt` tiene entrada en `conditions.json` (prueba unitaria en fase 11).

---

## FASE 8. Clasificador (`ml/CoffeeLeafClassifier.kt`)

El clasificador se divide en **preprocesado** (Bitmap → bytes RGB 224×224) e **inferencia** (bytes → probabilidades). Así la inferencia se puede probar con los `.rgb` de referencia, aislada de decodificación y escalado.

```kotlin
data class Prediction(val label: String, val confidence: Float)
data class ClassificationResult(
    val top: List<Prediction>,    // top-3, orden descendente
    val accepted: Boolean,        // top[0].confidence >= umbral
    val inferenceMs: Long
)

class CoffeeLeafClassifier(context: Context) : AutoCloseable {
    private val labels = context.assets.open("labels.txt").bufferedReader()
        .readLines().filter { it.isNotBlank() }
    val threshold: Float = readThreshold(context)            // de threshold.json
    private val interpreter = Interpreter(loadModel(context), Interpreter.Options().setNumThreads(4))
    private val input = ByteBuffer.allocateDirect(4 * SIZE * SIZE * 3).order(ByteOrder.nativeOrder())
    private val pixels = IntArray(SIZE * SIZE)

    /** Entrada de la app: foto vertical, cualquier tamaño. Hilo de fondo. */
    @Synchronized
    fun classify(bitmap: Bitmap): ClassificationResult {
        val scaled = Bitmap.createScaledBitmap(bitmap, SIZE, SIZE, true)   // squash
        scaled.getPixels(pixels, 0, SIZE, 0, 0, SIZE, SIZE)
        if (scaled !== bitmap) scaled.recycle()
        input.rewind()
        for (p in pixels) {                                  // RGB, 0..255, sin normalizar
            input.putFloat(((p shr 16) and 0xFF).toFloat())
            input.putFloat(((p shr 8) and 0xFF).toFloat())
            input.putFloat((p and 0xFF).toFloat())
        }
        return runInference()
    }

    /** Entrada para pruebas: 224*224*3 bytes RGB ya redimensionados. */
    @Synchronized
    fun classifyRgbBytes(rgb: ByteArray): ClassificationResult {
        require(rgb.size == SIZE * SIZE * 3)
        input.rewind()
        for (b in rgb) input.putFloat((b.toInt() and 0xFF).toFloat())
        return runInference()
    }

    private fun runInference(): ClassificationResult {
        val out = Array(1) { FloatArray(labels.size) }
        val t0 = SystemClock.elapsedRealtime()
        interpreter.run(input, out)
        val ms = SystemClock.elapsedRealtime() - t0
        val top = out[0].withIndex().sortedByDescending { it.value }.take(3)
            .map { Prediction(labels[it.index], it.value) }
        return ClassificationResult(top, top.first().confidence >= threshold, ms)
    }

    override fun close() = interpreter.close()
    private companion object { const val SIZE = 224 }
}
```

Notas:
- `Interpreter` **no es thread-safe**: una sola instancia, llamadas serializadas, siempre fuera del hilo principal.
- Crear el clasificador **una vez** (ViewModel), no por foto; cerrarlo en `onCleared()`.
- Cargar el modelo con `FileUtil.loadMappedFile` (librería de soporte) o con `assets.openFd` + `FileChannel.map`.
- Comprobar al iniciar que `output.size == labels.size`; si no, fallar con un mensaje claro.

`ImageUtils.kt`:
- Decodificar desde `Uri` con **muestreo previo** (`inSampleSize`) hasta que el lado menor quede entre 224 y ~600 px, y luego dejar que `createScaledBitmap` haga el escalado final. Reducir una foto de 12 MP de un golpe con filtro bilineal produce aliasing.
- Aplicar rotación **EXIF** (`ExifInterface`) en fotos de galería.
- Foto de CameraX: `ImageProxy.toBitmap()` **no** aplica rotación; rotar con `imageInfo.rotationDegrees` y **cerrar** el `ImageProxy`.
- Convertir siempre a `ARGB_8888`.

**Aceptación:** pruebas de la fase 11 en verde.

---

## FASE 9. Interfaz (Compose + CameraX)

Flujo con `NavHost`:
1. **HomeScreen:** título, instrucciones breves ("hoja sola, buena luz, enfocada, fondo simple"), botones "Tomar foto" y "Elegir de galería" (`PickVisualMedia`, no requiere permiso), aviso de herramienta de apoyo, enlace a "Acerca de" (versión del modelo, créditos de datasets).
2. **CameraScreen:** `Preview` + `ImageCapture` (`CAPTURE_MODE_MINIMIZE_LATENCY`), marco guía para la hoja, botón de captura, solicitud de permiso con `rememberLauncherForActivityResult(RequestPermission)` y pantalla explicativa si se deniega (con botón a ajustes).
3. **ResultScreen:** miniatura, nombre de la clase, confianza (barra), top-3, ficha de `conditions.json`, botón "Nueva foto". Si `accepted == false`: "No se pudo determinar con seguridad" y consejos de captura, sin ficha.

`ClassifierViewModel`:
- `sealed interface UiState { Idle; Loading; Success(result, bitmap); Error(msg) }` expuesto como `StateFlow`.
- `classify(bitmap)` en `viewModelScope.launch(Dispatchers.Default)`.
- Maneja errores (modelo no carga, URI inválida, `OutOfMemoryError`) sin cerrar la app.
- El bitmap grande no debe vivir más de lo necesario; guardar una miniatura (~512 px) para la pantalla de resultado.

Accesibilidad: `contentDescription` en imágenes y botones, contraste suficiente, textos desde `strings.xml`.

**Aceptación:** flujo foto → resultado completo en dispositivo/emulador; rotar la pantalla no pierde el estado.

---

## FASE 10. Rendimiento y robustez

- Cargar el modelo al crear el ViewModel, en hilo de fondo.
- Probar `setNumThreads(2)` vs `4`; el delegado GPU es opcional y solo se adopta si mejora la latencia **sin cambiar las predicciones** (comparar con los vectores de referencia).
- Casos a manejar: permiso denegado, imagen enorme, poca memoria, archivo corrupto, cámara no disponible.
- Verificar que el APK no contenga `INTERNET` (`aapt dump permissions`).

---

## FASE 11. Pruebas

**Unitarias (`src/test`)**
- Selección de top-3 y regla de umbral con probabilidades simuladas.
- `labels.txt` ↔ `conditions.json`: toda clase tiene ficha.
- Parseo de `threshold.json`.

**Instrumentadas (`src/androidTest`)**
- **Nivel 1 – modelo aislado:** para cada `NN.rgb` de `assets/golden/`, `classifyRgbBytes` debe dar la misma clase y probabilidades que `probs_tflite` con diferencia máxima **< 0.01**.
- **Nivel 2 – flujo completo:** para cada `NN.jpg`, decodificar y `classify(bitmap)`; exigir que la clase coincida en **≥ 9 de 10** imágenes (la diferencia de decodificación/escalado impide exigir igualdad de probabilidades).
- **Latencia:** 5 inferencias de calentamiento + 50 medidas; guardar mediana y p95 en `latency.json` (`getExternalFilesDir`) junto con el modelo del dispositivo.
- `labels.size` == nº de salidas del modelo.

**Aceptación:** todas pasan en un dispositivo físico o emulador x86_64.

---

## FASE 12. Evaluación en campo y documentación

1. Instalar el APK en **al menos un teléfono de gama media**; anotar modelo y versión de Android.
2. Probar con **fotos reales tomadas por el humano** (no del dataset): sol directo, sombra, fondo complicado, hoja con y sin enfermedad. Registrar en una tabla: foto, clase real, predicción, confianza. Calcular la exactitud en campo con n pequeño y **decir que n es pequeño**.
3. Registrar latencia (mediana/p95), tamaño del APK y del `.tflite`.
4. `docs/resultados.md`: métricas por clase, matriz de confusión, comparación de modelos (si se hizo), cobertura vs. exactitud del umbral, latencia, tamaño, resultados en campo y **limitaciones**.
5. `README.md` con pasos para reproducir: instalar, `make data train eval tflite parity`, copiar a `assets/`, compilar y probar.
6. Estas cifras alimentan los resultados del artículo y del póster, que hoy no tienen resultados cuantitativos propios.

---

## 13. Riesgos conocidos

| Riesgo | Mitigación |
|---|---|
| Pocas clases en los datasets | v1 con 3 clases; ampliar con fotos propias en v2 |
| **Cambio de dominio:** RoCoLe es café Robusta y en Colombia predomina el arábica | probar con hojas locales (fase 12) y declararlo como limitación; DECAFIA (Santander) ayuda |
| Fuga de datos entre particiones | dividir por imagen original antes de aumentar; verificación por hash |
| Precisión alta en el dataset, baja en campo | evaluación con fotos reales y reporte honesto |
| Desajuste de preprocesamiento | contrato de la sección 4 + paridad en dos niveles |
| Cuantización degrada el modelo | comparar fp32 vs cuantizado en `parity.json` |
| Foto que no es una hoja | umbral de confianza; clase `no_hoja` en v1.1 |
| Confianza mal calibrada | elegir umbral con validación y medir cobertura vs. exactitud |
| Etiquetas ruidosas en DECAFIA | revisión manual de muestra (fase 1) y regla de clase dominante documentada |

## 14. Definición de terminado

- [ ] Fases 0–5 con sus archivos de salida y criterios cumplidos.
- [ ] La app compila (`assembleDebug`) y el flujo foto → resultado funciona sin internet.
- [ ] Pruebas unitarias e instrumentadas en verde (nivel 1 < 0.01; nivel 2 ≥ 9/10).
- [ ] `docs/resultados.md` solo con cifras reales y con limitaciones explícitas.
- [ ] `docs/bitacora.md` y `docs/decisiones.md` completos.
- [ ] `README.md` reproducible.

---

## Apéndice: prompt sugerido para el agente

> Lee `PLAN_Prototipo_Cafe_Kotlin.md` completo. Implementa fase por fase en el orden indicado y verifica los criterios de aceptación de cada una antes de seguir. Respeta el contrato de la sección 4 y las reglas de la sección 0. No inventes cifras ni datos; si falta un dataset, una herramienta o acceso de red, detente y dime qué necesitas. Al terminar cada fase, actualiza `docs/bitacora.md` y resúmeme qué creaste, qué comprobaste y qué no pudiste ejecutar.
