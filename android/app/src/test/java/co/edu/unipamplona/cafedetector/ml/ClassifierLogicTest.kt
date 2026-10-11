package co.edu.unipamplona.cafedetector.ml

import java.io.File
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

class ClassifierLogicTest {
    private val labels = listOf("minador", "roya", "sana")

    @Test
    fun topIsSortedByConfidenceDescending() {
        val result = buildResult(floatArrayOf(0.10f, 0.70f, 0.20f), labels, threshold = 0.5f, inferenceMs = 7)

        assertEquals(listOf("roya", "sana", "minador"), result.top.map { it.label })
        assertEquals(0.70f, result.top.first().confidence, 0f)
        assertEquals(7, result.inferenceMs)
    }

    @Test
    fun topKeepsAtMostThreeClasses() {
        val result = buildResult(floatArrayOf(0.4f, 0.3f, 0.2f, 0.1f), listOf("a", "b", "c", "d"), 0.5f, 0)

        assertEquals(listOf("a", "b", "c"), result.top.map { it.label })
    }

    @Test
    fun resultIsAcceptedAtOrAboveTheThreshold() {
        assertTrue(buildResult(floatArrayOf(0.6f, 0.3f, 0.1f), labels, 0.6f, 0).accepted)
        assertFalse(buildResult(floatArrayOf(0.59f, 0.31f, 0.1f), labels, 0.6f, 0).accepted)
    }

    @Test
    fun mismatchBetweenOutputsAndLabelsFailsClearly() {
        assertThrows(IllegalArgumentException::class.java) {
            buildResult(floatArrayOf(0.5f, 0.5f), labels, 0.5f, 0)
        }
    }

    private val fourLabels = listOf("arana_roja", "minador", "roya", "sana")
    private val doubtRule = DoubtRule(classes = listOf("arana_roja", "roya"), margin = 0.4f)

    @Test
    fun closeCallBetweenTheDoubtClassesIsFlagged() {
        val result = buildResult(floatArrayOf(0.50f, 0.02f, 0.45f, 0.03f), fourLabels, 0.4f, 0, doubtRule)

        assertTrue(result.accepted)
        assertTrue(result.doubt)
        assertEquals(listOf("arana_roja", "roya"), result.top.take(2).map { it.label })
    }

    @Test
    fun clearWinnerIsNotFlaggedEvenInsideTheDoubtPair() {
        val result = buildResult(floatArrayOf(0.20f, 0.02f, 0.75f, 0.03f), fourLabels, 0.4f, 0, doubtRule)

        assertFalse(result.doubt)
    }

    @Test
    fun closeCallWithAnotherClassIsNotFlagged() {
        val result = buildResult(floatArrayOf(0.02f, 0.03f, 0.50f, 0.45f), fourLabels, 0.4f, 0, doubtRule)

        assertFalse(result.doubt)
    }

    @Test
    fun withoutARuleNothingIsFlagged() {
        assertFalse(buildResult(floatArrayOf(0.50f, 0.02f, 0.45f, 0.03f), fourLabels, 0.4f, 0).doubt)
    }

    @Test
    fun thresholdJsonWithDoubtRuleIsParsed() {
        val config = parseThreshold(
            """{"threshold": 0.6, "model_version": "v3", "doubt": {"classes": ["arana_roja", "roya"], "margin": 0.4}}""",
        )

        assertEquals(listOf("arana_roja", "roya"), config.doubt?.classes)
        assertEquals(0.4f, config.doubt!!.margin, 0f)
    }

    @Test
    fun thresholdJsonIsParsed() {
        val config = parseThreshold("""{"threshold": 0.6, "model_version": "v1-2026-10"}""")

        assertEquals(0.6f, config.threshold, 0f)
        assertEquals("v1-2026-10", config.modelVersion)
    }

    @Test
    fun shippedThresholdJsonIsValid() {
        val config = parseThreshold(File("src/main/assets/threshold.json").readText())

        assertTrue(config.threshold in 0f..1f)
        assertTrue(config.modelVersion.isNotBlank())
    }

    @Test
    fun sampleSizeKeepsEnoughResolutionForTheModel() {
        assertEquals(1, ImageUtils.sampleSizeFor(800, 600))
        assertEquals(4, ImageUtils.sampleSizeFor(4000, 3000)) // 12 MP -> 1000x750
        assertEquals(1, ImageUtils.sampleSizeFor(224, 224))
    }
}
