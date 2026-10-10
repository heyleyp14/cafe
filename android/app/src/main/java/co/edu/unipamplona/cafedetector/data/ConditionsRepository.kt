package co.edu.unipamplona.cafedetector.data

import android.content.Context
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

/** Informative sheet for one class; the texts come from the project report. */
@Serializable
data class Condition(
    val nombre: String,
    val sintomas: String,
    val condiciones: String,
)

/** Parses conditions.json: one entry per label of labels.txt. */
fun parseConditions(json: String): Map<String, Condition> = Json.decodeFromString(json)

class ConditionsRepository(context: Context) {
    private val conditions: Map<String, Condition> =
        parseConditions(context.assets.open(ASSET_NAME).bufferedReader().use { it.readText() })

    fun forLabel(label: String): Condition? = conditions[label]

    private companion object {
        const val ASSET_NAME = "conditions.json"
    }
}
