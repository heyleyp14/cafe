package co.edu.unipamplona.cafedetector.ui

import org.junit.Assert.assertEquals
import org.junit.Test

class FormattingTest {
    @Test
    fun roundsToNearestWholePercent() {
        assertEquals(87, confidencePercent(0.874f))
        assertEquals(88, confidencePercent(0.875f))
        assertEquals(0, confidencePercent(0.004f))
    }

    @Test
    fun keepsBoundsExact() {
        assertEquals(0, confidencePercent(0f))
        assertEquals(100, confidencePercent(1f))
    }

    @Test
    fun clampsValuesOutsideTheProbabilityRange() {
        assertEquals(100, confidencePercent(1.0000001f))
        assertEquals(100, confidencePercent(1.2f))
        assertEquals(0, confidencePercent(-0.1f))
        assertEquals(0, confidencePercent(Float.NaN))
    }
}
