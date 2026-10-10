package co.edu.unipamplona.cafedetector.ui

import kotlin.math.roundToInt

/** Model probability (0..1) as a whole percentage, clamped so a rounding artefact never shows 101 or -1. */
fun confidencePercent(confidence: Float): Int =
    if (confidence.isNaN()) 0 else (confidence * 100f).roundToInt().coerceIn(0, 100)
