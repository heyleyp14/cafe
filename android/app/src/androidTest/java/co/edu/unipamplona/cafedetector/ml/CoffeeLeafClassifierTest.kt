package co.edu.unipamplona.cafedetector.ml

import android.content.Context
import android.os.Build
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import kotlin.math.abs
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.float
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

/** Parity against the golden vectors exported by ml/05_paridad_tflite.py, plus latency. */
@RunWith(AndroidJUnit4::class)
class CoffeeLeafClassifierTest {
    private class Golden(val file: String, val probabilities: List<Float>)

    private val appContext: Context = InstrumentationRegistry.getInstrumentation().targetContext
    private val testAssets = InstrumentationRegistry.getInstrumentation().context.assets
    private val labels = appContext.assets.open("labels.txt").bufferedReader().use { it.readLines() }
        .filter { it.isNotBlank() }
    private lateinit var classifier: CoffeeLeafClassifier

    @Before
    fun setUp() {
        classifier = CoffeeLeafClassifier(appContext)
    }

    @After
    fun tearDown() = classifier.close()

    private fun golden(): List<Golden> {
        val text = testAssets.open("golden/golden.json").bufferedReader().use { it.readText() }
        return Json.parseToJsonElement(text).jsonArray.map { entry ->
            Golden(
                entry.jsonObject.getValue("file").jsonPrimitive.content,
                entry.jsonObject.getValue("probs_tflite").jsonArray.map { it.jsonPrimitive.float },
            )
        }
    }

    private fun List<Float>.argmaxLabel(): String = labels[indices.maxByOrNull { this[it] }!!]

    @Test
    fun labelCountMatchesModelOutputs() {
        assertEquals(classifier.outputCount, classifier.labelCount)
        assertEquals(labels.size, classifier.outputCount)
    }

    /** Level 1: the model alone, fed the exact bytes Python used. */
    @Test
    fun rgbBytesGiveTheSameProbabilitiesAsPython() {
        val goldens = golden()
        assertEquals(10, goldens.size)
        val maxDifferences = goldens.associate { golden ->
            val rgb = testAssets.open("golden/${golden.file}.rgb").use { it.readBytes() }
            val result = classifier.classifyRgbBytes(rgb)

            assertEquals("class of ${golden.file}", golden.probabilities.argmaxLabel(), result.top.first().label)
            // The result only carries the top three classes, so those are the ones compared.
            golden.file to result.top.maxOf { abs(it.confidence - golden.probabilities[labels.indexOf(it.label)]) }
        }
        File(appContext.getExternalFilesDir(null), "parity_level1.json")
            .writeText(maxDifferences.entries.joinToString(", ", "{", "}") { "\"${it.key}\": ${it.value}" })
        val worst = maxDifferences.maxByOrNull { it.value }!!
        assertTrue("max probability difference is ${worst.value} in ${worst.key}; all: $maxDifferences", worst.value < 0.01f)
    }

    /** Level 2: full flow (decode + scale on Android). Probabilities may differ, the class should not. */
    @Test
    fun jpegFlowGivesTheSameClassInAtLeastNineOfTen() {
        val goldens = golden()
        val matches = goldens.count { golden ->
            val bitmap = ImageUtils.decodeUpright { testAssets.open("golden/${golden.file}.jpg") }
            assertNotNull("could not decode ${golden.file}.jpg", bitmap)
            classifier.classify(bitmap!!).top.first().label == golden.probabilities.argmaxLabel()
        }
        File(appContext.getExternalFilesDir(null), "parity_level2.json")
            .writeText("""{"matches": $matches, "images": ${goldens.size}}""")
        assertTrue("only $matches of ${goldens.size} classes match", matches >= 9)
    }

    @Test
    fun latencyIsMeasuredAndSaved() {
        val rgb = testAssets.open("golden/00.rgb").use { it.readBytes() }
        repeat(WARMUP_RUNS) { classifier.classifyRgbBytes(rgb) }
        val times = List(MEASURED_RUNS) { classifier.classifyRgbBytes(rgb).inferenceMs }.sorted()
        val median = (times[MEASURED_RUNS / 2 - 1] + times[MEASURED_RUNS / 2]) / 2.0
        val p95 = times[(MEASURED_RUNS * 95 + 99) / 100 - 1]

        val json = """{"device": "${Build.MANUFACTURER} ${Build.MODEL}", "android": "${Build.VERSION.RELEASE}", """ +
            """"abi": "${Build.SUPPORTED_ABIS.first()}", "threads": ${CoffeeLeafClassifier.DEFAULT_THREADS}, """ +
            """"warmup_runs": $WARMUP_RUNS, "measured_runs": $MEASURED_RUNS, "median_ms": $median, "p95_ms": $p95}"""
        val file = File(appContext.getExternalFilesDir(null), "latency.json")
        file.writeText(json)
        assertTrue(file.length() > 0)
    }

    private companion object {
        const val WARMUP_RUNS = 5
        const val MEASURED_RUNS = 50
    }
}
