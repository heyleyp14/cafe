package co.edu.unipamplona.cafedetector.data

import java.io.File
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ConditionsTest {
    // Unit tests run with the module directory as working directory.
    private val assets = File("src/main/assets")

    @Test
    fun everyLabelHasAConditionSheet() {
        val labels = File(assets, "labels.txt").readLines().filter { it.isNotBlank() }
        val conditions = parseConditions(File(assets, "conditions.json").readText())

        assertEquals(labels.toSet(), conditions.keys)
        labels.forEach { label ->
            assertTrue("empty name for $label", conditions.getValue(label).nombre.isNotBlank())
            assertTrue("empty symptoms for $label", conditions.getValue(label).sintomas.isNotBlank())
        }
    }
}
