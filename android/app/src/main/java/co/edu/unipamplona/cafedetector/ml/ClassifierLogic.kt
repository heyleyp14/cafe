package co.edu.unipamplona.cafedetector.ml

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

data class Prediction(val label: String, val confidence: Float)

data class ClassificationResult(
    val top: List<Prediction>, // top-3, descending
    val accepted: Boolean, // top[0].confidence >= threshold
    val inferenceMs: Long,
    // The two best classes are a pair the model is known to confuse and they are too close to call.
    val doubt: Boolean = false,
)

/** Pair of classes the model confuses; a result is doubtful when they lead by less than [margin]. */
@Serializable
data class DoubtRule(val classes: List<String>, val margin: Float)

/** Contents of threshold.json, written by the evaluation script. */
@Serializable
data class ThresholdConfig(
    val threshold: Float,
    @SerialName("model_version") val modelVersion: String,
    val doubt: DoubtRule? = null,
)

fun parseThreshold(json: String): ThresholdConfig = Json.decodeFromString(json)

/** Builds the result from raw model probabilities; index i belongs to labels[i]. */
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

private const val TOP_K = 3
