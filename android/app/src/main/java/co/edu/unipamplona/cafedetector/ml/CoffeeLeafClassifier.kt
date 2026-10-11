package co.edu.unipamplona.cafedetector.ml

import android.content.Context
import android.graphics.Bitmap
import android.os.SystemClock
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import org.tensorflow.lite.Interpreter

/**
 * On-device classifier. Create it once, call it off the main thread and close it when done:
 * Interpreter is not thread-safe, so every call is serialized.
 *
 * Model contract: float32 [1, 224, 224, 3], RGB, values 0..255. The model normalizes internally.
 */
class CoffeeLeafClassifier(context: Context, numThreads: Int = DEFAULT_THREADS) : AutoCloseable {
    private val labels = context.assets.open(LABELS_ASSET).bufferedReader().use { it.readLines() }
        .filter { it.isNotBlank() }
    private val config = parseThreshold(context.assets.open(THRESHOLD_ASSET).bufferedReader().use { it.readText() })
    val threshold: Float = config.threshold
    val modelVersion: String = config.modelVersion

    private val interpreter = Interpreter(loadModel(context), Interpreter.Options().setNumThreads(numThreads))
    private val input = ByteBuffer.allocateDirect(4 * SIZE * SIZE * 3).order(ByteOrder.nativeOrder())
    private val pixels = IntArray(SIZE * SIZE)

    val outputCount: Int = interpreter.getOutputTensor(0).shape().last()
    val labelCount: Int get() = labels.size

    init {
        check(outputCount == labels.size) {
            "Model outputs $outputCount classes but $LABELS_ASSET has ${labels.size}"
        }
    }

    /** App entry point: upright photo of any size. Call from a background thread. */
    @Synchronized
    fun classify(bitmap: Bitmap): ClassificationResult {
        val scaled = Bitmap.createScaledBitmap(bitmap, SIZE, SIZE, true) // squash
        scaled.getPixels(pixels, 0, SIZE, 0, 0, SIZE, SIZE)
        if (scaled !== bitmap) scaled.recycle()
        input.rewind()
        for (p in pixels) { // RGB, 0..255, not normalized
            input.putFloat(((p shr 16) and 0xFF).toFloat())
            input.putFloat(((p shr 8) and 0xFF).toFloat())
            input.putFloat((p and 0xFF).toFloat())
        }
        return runInference()
    }

    /** Test entry point: 224*224*3 RGB bytes already resized. */
    @Synchronized
    fun classifyRgbBytes(rgb: ByteArray): ClassificationResult {
        require(rgb.size == SIZE * SIZE * 3) { "Expected ${SIZE * SIZE * 3} bytes, got ${rgb.size}" }
        input.rewind()
        for (b in rgb) input.putFloat((b.toInt() and 0xFF).toFloat())
        return runInference()
    }

    private fun runInference(): ClassificationResult {
        val out = Array(1) { FloatArray(labels.size) }
        input.rewind()
        val t0 = SystemClock.elapsedRealtime()
        interpreter.run(input, out)
        val ms = SystemClock.elapsedRealtime() - t0
        return buildResult(out[0], labels, threshold, ms, config.doubt)
    }

    @Synchronized
    override fun close() = interpreter.close()

    private fun loadModel(context: Context): MappedByteBuffer =
        context.assets.openFd(MODEL_ASSET).use { descriptor ->
            FileInputStream(descriptor.fileDescriptor).channel.use { channel ->
                channel.map(FileChannel.MapMode.READ_ONLY, descriptor.startOffset, descriptor.declaredLength)
            }
        }

    companion object {
        const val SIZE = 224
        const val DEFAULT_THREADS = 4
        private const val MODEL_ASSET = "model.tflite"
        private const val LABELS_ASSET = "labels.txt"
        private const val THRESHOLD_ASSET = "threshold.json"
    }
}
