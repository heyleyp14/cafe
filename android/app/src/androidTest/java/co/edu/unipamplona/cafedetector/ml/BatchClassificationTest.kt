package co.edu.unipamplona.cafedetector.ml

import android.content.Context
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import java.util.Locale
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Runs every photo under <external files>/lote/<true class>/ through the same decode and
 * classify path the app uses, and writes lote_resultados.csv. Skipped when the folder is absent.
 *
 * Usage: adb push <folder with one subfolder per class> /sdcard/Android/data/<package>/files/lote
 */
@RunWith(AndroidJUnit4::class)
class BatchClassificationTest {
    private val appContext: Context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun classifyEveryPhotoInTheBatchFolder() {
        val root = File(appContext.getExternalFilesDir(null), "lote")
        val photos = root.listFiles { f -> f.isDirectory }.orEmpty().sortedBy { it.name }.flatMap { folder ->
            folder.listFiles { f -> f.extension.lowercase() in setOf("jpg", "jpeg", "png") }.orEmpty()
                .sortedBy { it.name }.map { folder.name to it }
        }
        assumeTrue("no photos under ${root.path}", photos.isNotEmpty())

        val lines = mutableListOf("foto,clase_real,prediccion,confianza")
        CoffeeLeafClassifier(appContext).use { classifier ->
            for ((trueClass, file) in photos) {
                val bitmap = ImageUtils.decodeUpright { file.inputStream() }
                if (bitmap == null) {
                    lines += "${file.name},$trueClass,ILEGIBLE,"
                    continue
                }
                val top = classifier.classify(bitmap).top.first()
                bitmap.recycle()
                lines += "${file.name},$trueClass,${top.label},${String.format(Locale.US, "%.4f", top.confidence)}"
            }
        }
        File(appContext.getExternalFilesDir(null), "lote_resultados.csv").writeText(lines.joinToString("\n") + "\n")
    }
}
