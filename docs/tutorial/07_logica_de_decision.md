# Capítulo 7: La lógica de decisión

La función pura que convierte cuatro probabilidades en una respuesta prudente.

## ¿Por qué existe?

El laboratorio del [capítulo 6](06_clasificador_en_el_telefono.md) entrega un informe técnico: cuatro números entre 0 y 1. Alguien tiene que leerlo y decidir **qué se le dice al usuario**. Piense en un juez que recibe el peritaje: puede dictar sentencia, puede decir "las pruebas apuntan a uno de estos dos" o puede declarar que no hay pruebas suficientes.

Si la app siempre mostrara la clase más probable, afirmaría con la misma seguridad un 95 % y un 35 %, y repetiría a ciegas la confusión conocida entre arañita roja y roya ([capítulo 4](04_evaluacion_umbral_y_duda.md)). En una herramienta que **no** es de diagnóstico, la prudencia es parte del producto.

## La idea principal

La decisión tiene tres posibles salidas:

1. **Duda**: las dos clases más probables son el par conocido (arañita roja y roya) y están separadas por menos del margen (0.4). La app muestra ambas.
2. **Incierto**: la confianza más alta está por debajo del umbral (0.60). La app no afirma nada y da consejos para tomar mejor la foto.
3. **Aceptado**: en cualquier otro caso, la app muestra la clase y su ficha.

El orden importa: **la duda se revisa antes que el umbral**. Nombrar a los dos candidatos es más útil que un genérico "no se pudo determinar". Es el mismo orden con que se midió la regla: "doubt rule first, then the 0.6 threshold" (`ml/outputs/final/regla_duda_modelo_final.json`).

La lógica está separada en una función **pura** (sin Android, sin pantalla, sin modelo), lo que permite probarla con pruebas unitarias rápidas en la JVM.

## Cómo funciona en este código

Vive en:
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ml/ClassifierLogic.kt`
- `android/app/src/test/java/co/edu/unipamplona/cafedetector/ml/ClassifierLogicTest.kt`
- `android/app/src/main/assets/threshold.json`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ui/Formatting.kt`

### Los datos

```kotlin
data class Prediction(val label: String, val confidence: Float)

data class ClassificationResult(
    val top: List<Prediction>, // top-3, descending
    val accepted: Boolean, // top[0].confidence >= threshold
    val inferenceMs: Long,
    val doubt: Boolean = false,
)
```

Y la configuración, que se lee de `threshold.json` con kotlinx.serialization:

```kotlin
@Serializable
data class DoubtRule(val classes: List<String>, val margin: Float)

@Serializable
data class ThresholdConfig(
    val threshold: Float,
    @SerialName("model_version") val modelVersion: String,
    val doubt: DoubtRule? = null,
)
```

`doubt` es opcional (`= null`): un `threshold.json` antiguo, sin regla de duda, sigue siendo válido. Así se mantiene compatible con versiones previas del modelo.

### `buildResult`, el corazón

```kotlin
fun buildResult(
    probabilities: FloatArray,
    labels: List<String>,
    threshold: Float,
    inferenceMs: Long,
    doubtRule: DoubtRule? = null,
): ClassificationResult {
    require(probabilities.size == labels.size) {
        "Model outputs ${probabilities.size} classes but labels.txt has ${labels.size}"
    }
    val top = probabilities.withIndex().sortedByDescending { it.value }.take(TOP_K)
        .map { Prediction(labels[it.index], it.value) }
    val doubt = doubtRule != null && top.size >= 2 &&
        setOf(top[0].label, top[1].label) == doubtRule.classes.toSet() &&
        top[0].confidence - top[1].confidence < doubtRule.margin
    return ClassificationResult(top, top.first().confidence >= threshold, inferenceMs, doubt)
}
```

Paso a paso:
- `require(...)`: si el modelo y `labels.txt` no coinciden en número de clases, falla con un mensaje claro (otra barrera del [contrato](01_contrato_del_modelo.md)).
- `withIndex()` conserva la posición de cada probabilidad, que es lo que la une a su etiqueta: `labels[it.index]`.
- Se ordena de mayor a menor y se toman las tres primeras (`TOP_K = 3`).
- `doubt`: hay regla, hay al menos dos clases, las dos primeras son **exactamente** el par de la regla (sin importar el orden, por eso se comparan como conjuntos con `setOf`) y su diferencia es menor que el margen.
- `accepted`: la primera supera o iguala el umbral.

Observe que `buildResult` calcula `doubt` y `accepted` por separado y **no** decide cuál gana. Esa prioridad (duda primero) la aplica la pantalla de resultado, como veremos en el [capítulo 9](09_las_pantallas.md).

### Las pruebas unitarias

`ClassifierLogicTest.kt` documenta el comportamiento con ejemplos concretos. Algunos:

```kotlin
@Test
fun resultIsAcceptedAtOrAboveTheThreshold() {
    assertTrue(buildResult(floatArrayOf(0.6f, 0.3f, 0.1f), labels, 0.6f, 0).accepted)
    assertFalse(buildResult(floatArrayOf(0.59f, 0.31f, 0.1f), labels, 0.6f, 0).accepted)
}

@Test
fun closeCallBetweenTheDoubtClassesIsFlagged() {
    val result = buildResult(floatArrayOf(0.50f, 0.02f, 0.45f, 0.03f), fourLabels, 0.4f, 0, doubtRule)
    assertTrue(result.accepted)
    assertTrue(result.doubt)
    ...
}
```

- La primera fija el borde del umbral: 0.6 se acepta, 0.59 no.
- La segunda muestra que un resultado puede estar **aceptado y en duda a la vez** (0.50 frente a 0.45 de roya): por eso hace falta una regla de prioridad en la pantalla.
- Otras pruebas comprueban que un ganador claro dentro del par no se marca como duda, que un empate cercano con *otra* clase tampoco, y que el `threshold.json` real de la app se puede leer (`shippedThresholdJsonIsValid`).

### Mostrar porcentajes sin sorpresas

`Formatting.kt` convierte la probabilidad en un porcentaje entero:

```kotlin
fun confidencePercent(confidence: Float): Int =
    if (confidence.isNaN()) 0 else (confidence * 100f).roundToInt().coerceIn(0, 100)
```

El `coerceIn(0, 100)` evita que un artefacto de redondeo muestre "101 %".

## Cómo se conecta

- Recibe las probabilidades del [clasificador en el teléfono](06_clasificador_en_el_telefono.md).
- Aplica el umbral y la regla de duda que calibró la [evaluación](04_evaluacion_umbral_y_duda.md).
- Su `ClassificationResult` viaja por el [ViewModel](08_estado_y_navegacion.md) hasta [las pantallas](09_las_pantallas.md).

## Resumen

`buildResult` ordena las probabilidades, se queda con las tres mejores y marca dos banderas independientes: `accepted` (umbral 0.60) y `doubt` (arañita roja frente a roya con margen menor que 0.4). Es una función pura, bien cubierta por pruebas unitarias. Ahora veremos cómo la app coordina la foto, el modelo y la pantalla.

Ver también: [Glosario](glosario.md)
