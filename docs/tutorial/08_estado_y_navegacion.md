# Capítulo 8: Estado y navegación de la app

Cómo la app coordina la foto, el modelo y las pantallas sin congelarse ni perder el resultado.

## ¿Por qué existe?

Piense en la recepción de un consultorio. Llega un paciente (una foto), recepción le asigna un turno, lo manda al laboratorio (el clasificador) y, cuando hay resultados, lo dirige a la sala correcta. Si cambia el turno del personal (el usuario gira el teléfono y Android reconstruye la pantalla), recepción no puede olvidar quién estaba esperando.

En Android esto tiene dos complicaciones reales:
- **El hilo principal** dibuja la pantalla. Si en él se carga un modelo de varios megabytes o se ejecuta la inferencia, la app se congela.
- **Las pantallas son efímeras.** Al rotar el teléfono, la `Activity` se destruye y se vuelve a crear. Cualquier dato guardado en ella se pierde.

## La idea principal

BioCafe usa el patrón **MVVM** (Modelo–Vista–ViewModel):

- Un **ViewModel** (`ClassifierViewModel`) es la recepción. Vive más que las pantallas (sobrevive a la rotación), es dueño del clasificador y publica un **estado** observable.
- El estado es una de cuatro posibilidades: `Idle` (nada todavía), `Loading` (analizando), `Success` (hay resultado) o `Error`.
- Las **pantallas** (la Vista, [capítulo 9](09_las_pantallas.md)) solo observan ese estado y lo dibujan; cuando el usuario hace algo, llaman a un método del ViewModel.
- Un **NavHost** en `MainActivity` decide qué pantalla se muestra: inicio, cámara o resultado.

## Cómo funciona en este código

Vive en:
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/ui/ClassifierViewModel.kt`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/MainActivity.kt`
- `android/app/src/main/java/co/edu/unipamplona/cafedetector/data/ConditionsRepository.kt`

### Los cuatro estados

```kotlin
sealed interface UiState {
    data object Idle : UiState
    data object Loading : UiState
    /** [bitmap] is the ~512 px thumbnail, never the full photo. */
    data class Success(val result: ClassificationResult, val bitmap: Bitmap) : UiState
    data class Error(@param:StringRes val message: Int) : UiState
}
```

Una `sealed interface` le dice al compilador que no existen más casos. Así, cuando una pantalla hace `when (state)`, Kotlin obliga a contemplar los cuatro. `Success` guarda la **miniatura**, no la foto completa, para no retener memoria.

El ViewModel guarda el estado en un `MutableStateFlow` privado y lo expone como `StateFlow` de solo lectura (`val state: StateFlow<UiState>`). Las pantallas lo observan con `collectAsStateWithLifecycle()` y se redibujan cada vez que cambia.

### Cargar el modelo sin congelar la app

```kotlin
// Mapping the model and creating the interpreter takes long enough to drop frames on the main thread.
private val loading: Job = viewModelScope.launch(Dispatchers.Default) {
    try {
        val conditions = ConditionsRepository(application)
        val classifier = CoffeeLeafClassifier(application)
        engine = Engine(classifier, conditions)
        _modelVersion.value = classifier.modelVersion
        ...
    } catch (t: Throwable) { // includes UnsatisfiedLinkError and OutOfMemoryError
        Log.e(TAG, "Model failed to load", t)
    }
}
```

Apenas se crea el ViewModel, una **corrutina** en `Dispatchers.Default` (un hilo de fondo) crea el clasificador y el repositorio de fichas (`ConditionsRepository`, que lee `conditions.json`). Si falla, no se cierra la app: `engine` queda en `null` y, cuando el usuario intente clasificar, verá un error amable.

### Clasificar: tres entradas, un solo camino

```kotlin
fun classify(bitmap: Bitmap) = launchClassification { bitmap }
fun classify(uri: Uri) = launchClassification { ImageUtils.decodeUpright(getApplication(), uri) }
fun classify(image: ImageProxy) = launchClassification { ImageUtils.fromImageProxy(image) }
```

Una foto de la galería (`Uri`), una de la cámara (`ImageProxy`) o un `Bitmap` ya listo terminan en el mismo `launchClassification`:

```kotlin
private fun launchClassification(load: () -> Bitmap?) {
    classification?.cancel()
    _state.value = UiState.Loading
    classification = viewModelScope.launch(Dispatchers.Default) {
        val outcome = try {
            analyse(load)
        } catch (e: CancellationException) {
            throw e
        } catch (e: OutOfMemoryError) {
            UiState.Error(R.string.error_out_of_memory)
        } catch (e: Exception) {
            UiState.Error(R.string.error_classification)
        }
        ensureActive() // a newer request owns the state now
        _state.value = outcome
    }
}
```

- `classification?.cancel()`: si el usuario elige otra foto mientras se analiza la anterior, la anterior se cancela.
- El estado pasa a `Loading` de inmediato, para que la pantalla muestre el indicador.
- Todo el trabajo pesado ocurre en el hilo de fondo.
- `ensureActive()` evita una condición de carrera: si llegó una petición más nueva, este resultado viejo no pisa el estado.
- Cada tipo de fallo se traduce a un mensaje distinto (imagen ilegible, memoria, modelo que no cargó).

Dentro de `analyse`, `loading.join()` espera a que el modelo termine de cargar, por si el usuario fue más rápido que la carga. Y el bloque `finally` libera la foto completa: solo la miniatura sobrevive.

### La navegación

`MainActivity.kt` define tres rutas y comparte **un solo** ViewModel entre ellas:

```kotlin
/** [viewModel] is scoped to the Activity, so the three screens share it and it survives rotation. */
@Composable
private fun CafeDetectorApp(viewModel: ClassifierViewModel = viewModel()) {
    ...
    NavHost(navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) { ... }
        composable(Routes.CAMERA) { ... }
        composable(Routes.RESULT) { ... }
    }
}
```

Cuando la cámara captura una foto, llama a `viewModel.classify(image)` y navega a resultado con `popUpTo(Routes.HOME)`: así, el botón "atrás" desde el resultado vuelve al inicio, no a la cámara.

Un caso borde bien resuelto:

```kotlin
// After process death the back stack is restored but the result is gone.
LaunchedEffect(state) { if (state is UiState.Idle) backHome() }
```

Si Android mata el proceso en segundo plano y el usuario vuelve, la pila de pantallas se restaura pero el resultado ya no existe. En vez de mostrar una pantalla vacía, la app regresa al inicio.

## Cómo se conecta

- **Carga y usa** el [clasificador en el teléfono](06_clasificador_en_el_telefono.md), que a su vez produce el resultado de [la lógica de decisión](07_logica_de_decision.md).
- **Publica el estado** que dibujan [las pantallas](09_las_pantallas.md), y ellas le **envían las fotos**.

## Resumen

`ClassifierViewModel` es dueño del clasificador, trabaja en hilos de fondo con corrutinas y publica un estado de cuatro casos que sobrevive a la rotación; `MainActivity` conecta tres pantallas con un `NavHost` y un único ViewModel compartido. Falta ver qué ve el usuario en cada una.

Ver también: [Glosario](glosario.md)
