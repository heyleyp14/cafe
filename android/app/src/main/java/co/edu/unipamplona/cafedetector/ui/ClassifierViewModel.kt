package co.edu.unipamplona.cafedetector.ui

import android.app.Application
import android.graphics.Bitmap
import android.net.Uri
import android.util.Log
import androidx.annotation.StringRes
import androidx.camera.core.ImageProxy
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import co.edu.unipamplona.cafedetector.R
import co.edu.unipamplona.cafedetector.data.Condition
import co.edu.unipamplona.cafedetector.data.ConditionsRepository
import co.edu.unipamplona.cafedetector.ml.ClassificationResult
import co.edu.unipamplona.cafedetector.ml.CoffeeLeafClassifier
import co.edu.unipamplona.cafedetector.ml.ImageUtils
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

sealed interface UiState {
    data object Idle : UiState
    data object Loading : UiState

    /** [bitmap] is the ~512 px thumbnail, never the full photo. */
    data class Success(val result: ClassificationResult, val bitmap: Bitmap) : UiState

    data class Error(@param:StringRes val message: Int) : UiState
}

/** Owns the classifier for the whole Activity, so the state survives rotation. */
class ClassifierViewModel(application: Application) : AndroidViewModel(application) {
    private class Engine(val classifier: CoffeeLeafClassifier, val conditions: ConditionsRepository)

    private val _state = MutableStateFlow<UiState>(UiState.Idle)
    val state: StateFlow<UiState> = _state.asStateFlow()

    private val _modelVersion = MutableStateFlow<String?>(null)

    /** Null while the model is loading or if it failed to load. */
    val modelVersion: StateFlow<String?> = _modelVersion.asStateFlow()

    @Volatile
    private var engine: Engine? = null

    // Mapping the model and creating the interpreter takes long enough to drop frames on the main thread.
    private val loading: Job = viewModelScope.launch(Dispatchers.Default) {
        try {
            val conditions = ConditionsRepository(application)
            val classifier = CoffeeLeafClassifier(application)
            engine = Engine(classifier, conditions)
            _modelVersion.value = classifier.modelVersion
            // onCleared() may have run before the field was set; it would have had nothing to close.
            if (!isActive) classifier.close()
        } catch (t: Throwable) { // includes UnsatisfiedLinkError and OutOfMemoryError
            Log.e(TAG, "Model failed to load", t)
        }
    }

    private var classification: Job? = null

    /** Takes ownership of [bitmap]: it is recycled once the thumbnail exists. */
    fun classify(bitmap: Bitmap) = launchClassification { bitmap }

    fun classify(uri: Uri) = launchClassification { ImageUtils.decodeUpright(getApplication(), uri) }

    /** Takes ownership of [image]; it is decoded, rotated and closed off the main thread. */
    fun classify(image: ImageProxy) = launchClassification { ImageUtils.fromImageProxy(image) }

    fun conditionFor(label: String): Condition? = engine?.conditions?.forLabel(label)

    private fun launchClassification(load: () -> Bitmap?) {
        classification?.cancel()
        _state.value = UiState.Loading
        classification = viewModelScope.launch(Dispatchers.Default) {
            val outcome = try {
                analyse(load)
            } catch (e: CancellationException) {
                throw e
            } catch (e: OutOfMemoryError) {
                Log.e(TAG, "Out of memory while classifying", e)
                UiState.Error(R.string.error_out_of_memory)
            } catch (e: Exception) {
                Log.e(TAG, "Classification failed", e)
                UiState.Error(R.string.error_classification)
            }
            ensureActive() // a newer request owns the state now
            _state.value = outcome
        }
    }

    private suspend fun analyse(load: () -> Bitmap?): UiState {
        // Loaded before waiting for the model so an ImageProxy is always consumed and closed.
        val photo = try {
            load()
        } catch (e: Exception) { // unreadable URI: SecurityException, FileNotFoundException, IOException...
            Log.e(TAG, "Image could not be decoded", e)
            null
        } ?: return UiState.Error(R.string.error_image_unreadable)

        var thumbnail: Bitmap? = null
        try {
            loading.join()
            val engine = engine ?: return UiState.Error(R.string.error_model_load)
            val result = engine.classifier.classify(photo)
            return UiState.Success(result, ImageUtils.thumbnail(photo).also { thumbnail = it })
        } finally {
            // Only the thumbnail may outlive the classification; a small photo is its own thumbnail.
            if (thumbnail !== photo) photo.recycle()
        }
    }

    override fun onCleared() {
        engine?.classifier?.close()
    }

    private companion object {
        const val TAG = "ClassifierViewModel"
    }
}
