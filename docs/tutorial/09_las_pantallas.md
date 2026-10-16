# Capítulo 9: Las pantallas

Lo que ve el usuario: inicio, cámara y resultado, construidos con Jetpack Compose.

## ¿Por qué existe?

Todo lo anterior es invisible para el caficultor. Lo que él ve son tres vitrinas: una que lo invita a traer una hoja, otra que le ayuda a encuadrarla y otra que le explica la respuesta. Si la última dijera "roya 51 %" sin más, el usuario podría tomar una decisión equivocada; por eso la pantalla de resultado es la que más cuidado lleva: muestra la duda cuando existe, reconoce cuando el modelo no está seguro y siempre recuerda que no es un diagnóstico.

## La idea principal

Las pantallas están escritas con **Jetpack Compose**: en lugar de diseñar en XML, se escriben funciones Kotlin marcadas con `@Composable` que describen la interfaz a partir del estado. Cuando el estado cambia, Compose vuelve a dibujar lo necesario.

Cada pantalla es "tonta" a propósito: recibe datos y funciones (`onTakePhoto`, `onImagePicked`...) y no sabe nada del modelo. Toda la lógica está en el [ViewModel](08_estado_y_navegacion.md) y en [la lógica de decisión](07_logica_de_decision.md).

## Cómo funciona en este código

Vive en:
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ui/HomeScreen.kt`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ui/CameraScreen.kt`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ui/ResultScreen.kt`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ui/Components.kt`
- `android/app/src/main/assets/conditions.json` y `data/ConditionsRepository.kt`

### Inicio: dos maneras de traer una hoja

`HomeScreen` muestra consejos para tomar la foto (una sola hoja, buena luz, imagen enfocada, fondo simple), un botón para la cámara y otro para la galería. La galería usa el selector de fotos del sistema:

```kotlin
// The system photo picker grants access to the chosen image only, so no storage permission is needed.
val picker = rememberLauncherForActivityResult(PickVisualMedia()) { uri -> uri?.let(onImagePicked) }
```

Gracias a `PickVisualMedia`, la app no necesita permiso de almacenamiento: el sistema le entrega solo la imagen elegida. El diálogo "Acerca de" muestra la versión del modelo que viene de `threshold.json` (ver el [contrato](01_contrato_del_modelo.md)) y los créditos de los datasets.

### Cámara: CameraX con un marco guía

`CameraScreen` pide el permiso de cámara, y si el usuario lo niega le ofrece ir a los ajustes. Al volver, lo comprueba de nuevo (`LifecycleEventEffect(Lifecycle.Event.ON_RESUME)`).

La captura se configura con **CameraX**:

```kotlin
// The model sees 224x224, so a full-sensor capture would only cost memory and decode time.
private val CAPTURE_SIZE = Size(1280, 960)
...
ImageCapture.Builder()
    .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
    .setResolutionSelector(...ResolutionStrategy(CAPTURE_SIZE, ...))
```

Pedir la resolución completa del sensor sería desperdiciar memoria, porque el modelo solo ve 224×224. Luego:

```kotlin
val selector = listOf(CameraSelector.DEFAULT_BACK_CAMERA, CameraSelector.DEFAULT_FRONT_CAMERA)
    .first { provider.hasCamera(it) } // throws when the device has no camera at all
provider.bindToLifecycle(lifecycleOwner, selector, preview, imageCapture)
```

`bindToLifecycle` ata la cámara al ciclo de vida de la pantalla: se apaga sola cuando el usuario sale. Sobre la vista previa se dibujan cuatro esquinas blancas (`LeafGuideFrame`) que indican dónde poner la hoja sin taparla. Al pulsar el botón, `takePicture` entrega un `ImageProxy` que se pasa al ViewModel; él lo gira, lo clasifica y lo cierra ([capítulo 6](06_clasificador_en_el_telefono.md)).

### Resultado: tres respuestas posibles

Este es el fragmento clave de `ResultScreen.kt`:

```kotlin
is UiState.Success ->
    // Doubt goes first: naming the two candidates is more useful than a generic "could not tell".
    when {
        state.result.doubt -> DoubtResult(state.result, state.bitmap, conditionFor, modifier)
        !state.result.accepted -> UncertainResult(state.result, state.bitmap, modifier)
        else -> AcceptedResult(state.result, state.bitmap, conditionFor, modifier)
    }
```

Aquí se aplica la prioridad que vimos en el [capítulo 7](07_logica_de_decision.md): **primero la duda, después el umbral**.

- **`AcceptedResult`**: miniatura, nombre de la clase, barra de confianza, las tres clases más probables y la **ficha** de la afectación (síntomas y condiciones favorables).
- **`DoubtResult`**: el título "Puede ser X o Y", un mensaje que invita a comparar la hoja con los síntomas de cada una, las dos probabilidades y la ficha de síntomas de ambas.
- **`UncertainResult`**: "No se pudo determinar con seguridad", la confianza obtenida y consejos para repetir la foto. No se muestra ninguna clase.

Cuando el estado es `Loading`, se ve un indicador circular; cuando es `Error`, un panel con el mensaje y un botón para volver.

### Las fichas informativas

Los textos de cada clase están en `android/app/src/main/assets/conditions.json`, uno por etiqueta de `labels.txt`:

```json
"arana_roja": {
  "nombre": "Arañita roja del café",
  "sintomas": "Hojas con pérdida de su brillo natural ...",
  "condiciones": "Las condiciones que favorecen ..."
}
```

`ConditionsRepository` los carga con kotlinx.serialization y la pantalla los pide con `conditionFor(label)`. `docs/decisiones.md` registra que los textos salen del informe del proyecto, y una regla del plan prohíbe dar recomendaciones de manejo (fungicidas, dosis) que no estén en él.

### El aviso que siempre aparece

`Components.kt` define `SupportNotice`, que las tres variantes de resultado incluyen al final. Su texto (en `res/values/strings.xml`) es: "Prototipo académico de apoyo. No es una herramienta de diagnóstico." Cumple la regla 7 del plan, que exige decirlo en pantalla.

## Cómo se conecta

- **Envían fotos** al [ViewModel](08_estado_y_navegacion.md) y dibujan el estado que él **publica**.
- Muestran el `ClassificationResult` que produce [la lógica de decisión](07_logica_de_decision.md).
- Terminan dentro del APK que distribuye la [orquestación y entrega](10_orquestacion_y_entrega.md).

## Resumen

Tres pantallas Compose: inicio (cámara o galería, sin permiso de almacenamiento), cámara (CameraX a 1280×960 con un marco guía) y resultado, que elige entre duda, incierto y aceptado en ese orden, muestra la ficha de `conditions.json` y siempre recuerda que no es un diagnóstico. El último capítulo explica cómo se ensambla y se entrega todo.

Ver también: [Glosario](glosario.md)
