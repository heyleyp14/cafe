package co.edu.unipamplona.cafedetector.ml

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

data class Prediction(val label: String, val confidence: Float)

data class ClassificationResult(
    val top: List<Prediction>, // top-3, descending
    val accepted: Boolean, // top[0].confidence >= threshold
    val inferenceMs: Long,
)

/** Contents of threshold.json, written by the evaluation script. */
@Serializable
data class ThresholdConfig(
    val threshold: Float,
    @SerialName("model_version") val modelVersion: String,
)

fun parseThreshold(json: String): ThresholdConfig = Json.decodeFromString(json)

/** Builds the result from raw model probabilities; index i belongs to labels[i]. */
fun buildResult(
    probabilities: FloatArray,
    labels: List<String>,
    threshold: Float,
    inferenceMs: Long,
): ClassificationResult {
    require(probabilities.size == labels.size) {
        "Model outputs ${probabilities.size} classes but labels.txt has ${labels.size}"
    }
    val top = probabilities.withIndex().sortedByDescending { it.value }.take(TOP_K)
        .map { Prediction(labels[it.index], it.value) }
    return ClassificationResult(top, top.first().confidence >= threshold, inferenceMs)
}

private const val TOP_K = 3
