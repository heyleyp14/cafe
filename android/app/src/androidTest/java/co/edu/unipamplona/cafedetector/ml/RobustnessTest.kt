package co.edu.unipamplona.cafedetector.ml

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import android.os.Build
import androidx.exifinterface.media.ExifInterface
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

/** Phase 10: awkward inputs and the thread-count comparison. */
@RunWith(AndroidJUnit4::class)
class RobustnessTest {
    private val appContext: Context = InstrumentationRegistry.getInstrumentation().targetContext
    private val testAssets = InstrumentationRegistry.getInstrumentation().context.assets

    private fun jpeg(width: Int, height: Int): ByteArray {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565).apply { eraseColor(Color.rgb(40, 120, 60)) }
        return ByteArrayOutputStream().also { bitmap.compress(Bitmap.CompressFormat.JPEG, 90, it); bitmap.recycle() }
            .toByteArray()
    }

    @Test
    fun corruptFileIsRejectedInsteadOfCrashing() {
        val garbage = ByteArray(4096) { (it * 31).toByte() }
        assertNull(ImageUtils.decodeUpright { ByteArrayInputStream(garbage) })
        assertNull(ImageUtils.decodeUpright { ByteArrayInputStream(ByteArray(0)) })
        assertNull(ImageUtils.decodeUpright { null })
    }

    @Test
    fun truncatedJpegDoesNotCrash() {
        val bytes = jpeg(800, 600)
        // The decoder may return a partial image or nothing; either is fine, an exception is not.
        ImageUtils.decodeUpright { ByteArrayInputStream(bytes.copyOf(bytes.size / 3)) }?.recycle()
    }

    @Test
    fun hugeImageIsSubsampledBeforeClassification() {
        val bytes = jpeg(4000, 3000) // 12 MP
        val bitmap = ImageUtils.decodeUpright { ByteArrayInputStream(bytes) }
        assertNotNull(bitmap)
        assertEquals(1000, bitmap!!.width)
        assertEquals(750, bitmap.height)
        assertEquals(Bitmap.Config.ARGB_8888, bitmap.config)
        CoffeeLeafClassifier(appContext).use { assertEquals(3, it.classify(bitmap).top.size) }
    }

    @Test
    fun exifRotationIsApplied() {
        val file = File(appContext.cacheDir, "exif_rotated.jpg").apply { writeBytes(jpeg(600, 480)) }
        ExifInterface(file).apply {
            setAttribute(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_ROTATE_90.toString())
            saveAttributes()
        }
        val bitmap = ImageUtils.decodeUpright { file.inputStream() }
        file.delete()
        assertNotNull(bitmap)
        assertEquals(480, bitmap!!.width)
        assertEquals(600, bitmap.height)
    }

    @Test
    fun threadCountChangesLatencyButNotPredictions() {
        val files = (0..9).map { "%02d".format(it) }
        val inputs = files.map { name -> testAssets.open("golden/$name.rgb").use { it.readBytes() } }
        val results = listOf(2, 4).associateWith { threads ->
            CoffeeLeafClassifier(appContext, threads).use { classifier ->
                val labels = inputs.map { classifier.classifyRgbBytes(it).top.first().label }
                repeat(WARMUP_RUNS) { classifier.classifyRgbBytes(inputs[0]) }
                val times = List(MEASURED_RUNS) { classifier.classifyRgbBytes(inputs[0]).inferenceMs }.sorted()
                Triple(labels, (times[MEASURED_RUNS / 2 - 1] + times[MEASURED_RUNS / 2]) / 2.0, times[(MEASURED_RUNS * 95 + 99) / 100 - 1])
            }
        }
        val json = results.entries.joinToString(", ", """{"device": "${Build.MANUFACTURER} ${Build.MODEL}", """, "}") {
            """"threads_${it.key}": {"median_ms": ${it.value.second}, "p95_ms": ${it.value.third}}"""
        }
        File(appContext.getExternalFilesDir(null), "latency_threads.json").writeText(json)
        assertEquals(results.getValue(2).first, results.getValue(4).first)
        assertTrue(results.values.all { it.second >= 0 })
    }

    private companion object {
        const val WARMUP_RUNS = 5
        const val MEASURED_RUNS = 50
    }
}
