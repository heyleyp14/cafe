# Capítulo 6: El clasificador en el teléfono

El código Kotlin que convierte una foto en cuatro probabilidades, sin internet.

## ¿Por qué existe?

Hasta ahora todo ocurrió en Python. Pero el caficultor tiene un teléfono, no un computador con TensorFlow. Necesitamos un **laboratorio portátil** dentro de la app: alguien que reciba la foto tal como viene (de la cámara o de la galería, de cualquier tamaño, quizá girada), la prepare exactamente como pide el [contrato](01_contrato_del_modelo.md) y se la entregue al modelo.

Si ese laboratorio se equivoca en un detalle (no endereza la foto, cambia el orden de los colores, normaliza dos veces), el modelo responde mal sin dar ningún error. Por eso esta parte es pequeña, cuidadosa y está muy probada.

## La idea principal

Dos piezas se reparten el trabajo:

- **`ImageUtils`** prepara la foto: la decodifica sin agotar la memoria, aplica la rotación EXIF (galería) o la rotación de la cámara, y hace una miniatura para la pantalla de resultado.
- **`CoffeeLeafClassifier`** ejecuta el modelo: carga `model.tflite`, `labels.txt` y `threshold.json` desde los *assets*, aplasta la foto a 224×224, llena el búfer de entrada con valores RGB 0–255 y llama al `Interpreter` de LiteRT.

## Cómo funciona en este código

Vive en:
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ml/CoffeeLeafClassifier.kt`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ml/ImageUtils.kt`
- `android/app/src/androidTest/java/co/edu/unipamplona/cafedetector/ml/RobustnessTest.kt`
- `android/app/build.gradle.kts`, `android/gradle/libs.versions.toml`, `android/app/src/main/AndroidManifest.xml`

### Cargar el modelo sin copiarlo

```kotlin
private fun loadModel(context: Context): MappedByteBuffer =
    context.assets.openFd(MODEL_ASSET).use { descriptor ->
        FileInputStream(descriptor.fileDescriptor).channel.use { channel ->
            channel.map(FileChannel.MapMode.READ_ONLY, descriptor.startOffset, descriptor.declaredLength)
        }
    }
```

El modelo no se lee a memoria: se **mapea** directamente desde el APK (`FileChannel.map`). Para que eso funcione, el archivo no puede ir comprimido dentro del APK, y por eso `android/app/build.gradle.kts` declara:

```kotlin
// The model is memory-mapped from the APK, so it must stay uncompressed.
androidResources {
    noCompress += "tflite"
}
```

El intérprete, y la API para usarlo desde Kotlin, vienen de LiteRT 2.3.0 (`android/gradle/libs.versions.toml`). `docs/decisiones.md` registra un detalle curioso: aunque la librería se llama LiteRT, la clase que contiene esa versión es `org.tensorflow.lite.Interpreter`, y ese es el import válido.

```kotlin
private val interpreter = Interpreter(loadModel(context), Interpreter.Options().setNumThreads(numThreads))
private val input = ByteBuffer.allocateDirect(4 * SIZE * SIZE * 3).order(ByteOrder.nativeOrder())
```

El búfer de entrada mide `4 × 224 × 224 × 3` bytes: 4 bytes por cada `float32`. Se reserva una sola vez y se reutiliza en cada foto.

### Clasificar una foto

```kotlin
@Synchronized
fun classify(bitmap: Bitmap): ClassificationResult {
    val scaled = Bitmap.createScaledBitmap(bitmap, SIZE, SIZE, true) // squash
    scaled.getPixels(pixels, 0, SIZE, 0, 0, SIZE, SIZE)
    if (scaled !== bitmap) scaled.recycle()
    input.rewind()
    for (p in pixels) { // RGB, 0..255, not normalized
        input.putFloat(((p shr 16) and 0xFF).toFloat())
        input.putFloat(((p shr 8) and 0xFF).toFloat())
        input.putFloat((p and 0xFF).toFloat())
    }
    return runInference()
}
```

Línea por línea:
- `createScaledBitmap(..., SIZE, SIZE, true)` aplasta la foto a 224×224 (el "squash" del contrato).
- `getPixels` copia los píxeles a un arreglo de enteros ARGB.
- El bucle separa rojo, verde y azul y los escribe como flotantes 0–255. **No** divide entre 255: la normalización va dentro del modelo.
- `@Synchronized` hace que dos llamadas no usen el intérprete a la vez, porque el `Interpreter` no es seguro entre hilos (lo dice el comentario de la clase).

`runInference` mide el tiempo y le pasa las probabilidades a `buildResult`, la función de decisión que veremos en el [capítulo 7](07_logica_de_decision.md):

```kotlin
val t0 = SystemClock.elapsedRealtime()
interpreter.run(input, out)
val ms = SystemClock.elapsedRealtime() - t0
return buildResult(out[0], labels, threshold, ms, config.doubt)
```

Existe también `classifyRgbBytes`, una puerta de entrada solo para pruebas que recibe los bytes ya redimensionados del archivo `.rgb` (nivel 1 de paridad, [capítulo 5](05_conversion_y_paridad.md)).

### Enderezar y reducir la foto: `ImageUtils`

Una foto de 12 MP decodificada completa ocupa mucha memoria. `decodeUpright` primero lee solo las dimensiones y luego decodifica con submuestreo:

```kotlin
/** Largest power-of-two subsampling that keeps the shorter side >= MIN_SHORT_SIDE. */
fun sampleSizeFor(width: Int, height: Int): Int {
    var sample = 1
    while (minOf(width, height) / (sample * 2) >= MIN_SHORT_SIDE) sample *= 2
    return sample
}
```

Con `MIN_SHORT_SIDE = 448`, el lado corto nunca baja de 448 píxeles: suficiente para que el paso final a 224 no tenga que ampliar la imagen. La prueba unitaria `sampleSizeKeepsEnoughResolutionForTheModel` comprueba que una foto de 4000×3000 se decodifica con factor 4.

Después se lee la etiqueta EXIF de orientación y se aplica el giro o espejo correspondiente (`applyExifOrientation`). Para las fotos de la cámara, `fromImageProxy` aplica `rotationDegrees`, porque `toBitmap()` de CameraX no gira la imagen. Así se cumple la regla del contrato: "la imagen llega a la app ya en posición vertical".

### Pruebas de robustez

`RobustnessTest.kt` (instrumentada) prueba entradas incómodas: un archivo corrupto se rechaza sin cerrar la app, un JPEG truncado no provoca excepción, una imagen de 12 MP se submuestrea, la rotación EXIF se aplica, y cambiar el número de hilos cambia la latencia pero no las predicciones.

### Rendimiento

Según `ml/outputs/final/android_phone/latency.json`, en un motorola edge 30 (Android 14, arm64-v8a), con 4 hilos, 5 corridas de calentamiento y 50 medidas, la inferencia tarda una mediana de 48.0 ms (p95 de 49 ms).

### Sin internet, de verdad

`AndroidManifest.xml` solo pide el permiso de cámara, y **quita** explícitamente los permisos que añaden las dependencias de LiteRT:

```xml
<!-- No INTERNET permission on purpose: inference runs fully on the device. -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" tools:node="remove" />
```

`docs/decisiones.md` explica el motivo: la app no usa red ni tareas en segundo plano, y una app sin conexión no debería declarar permisos que no necesita.

## Cómo se conecta

- Aplica el preprocesamiento que **dicta** el [contrato del modelo](01_contrato_del_modelo.md).
- Ejecuta el `model.tflite` que entrega la [conversión](05_conversion_y_paridad.md).
- **Pasa las probabilidades** a [la lógica de decisión](07_logica_de_decision.md).
- Lo **carga y usa** el [ViewModel](08_estado_y_navegacion.md).

## Resumen

`ImageUtils` endereza y reduce la foto sin agotar la memoria; `CoffeeLeafClassifier` la aplasta a 224×224, la convierte en flotantes RGB 0–255 y ejecuta el intérprete de LiteRT sobre un modelo mapeado desde el APK. El resultado son cuatro probabilidades. Qué decirle al usuario con ellas es tarea del siguiente capítulo.

Ver también: [Glosario](glosario.md)
