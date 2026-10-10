package co.edu.unipamplona.cafedetector.ml

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.camera.core.ImageProxy
import androidx.exifinterface.media.ExifInterface
import java.io.InputStream

object ImageUtils {
    // The decoded image keeps its shorter side at or above this, so the final
    // createScaledBitmap to 224 never upscales and never downsamples a 12 MP photo in one step.
    private const val MIN_SHORT_SIDE = 448
    private const val THUMBNAIL_SIDE = 512

    /** Decodes a gallery image upright (EXIF applied) with pre-sampling. Null if it cannot be read. */
    fun decodeUpright(context: Context, uri: Uri): Bitmap? = decodeUpright { context.contentResolver.openInputStream(uri) }

    /** Same as above for any re-openable source; used by tests to decode assets. */
    fun decodeUpright(open: () -> InputStream?): Bitmap? {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        // With inJustDecodeBounds the decoder returns null by design; only the bounds matter here.
        (open() ?: return null).use { BitmapFactory.decodeStream(it, null, bounds) }
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null

        val options = BitmapFactory.Options().apply {
            inSampleSize = sampleSizeFor(bounds.outWidth, bounds.outHeight)
            inPreferredConfig = Bitmap.Config.ARGB_8888
        }
        val bitmap = open()?.use { BitmapFactory.decodeStream(it, null, options) } ?: return null
        val orientation = open()?.use {
            ExifInterface(it).getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL)
        } ?: ExifInterface.ORIENTATION_NORMAL
        return applyExifOrientation(bitmap.toArgb8888(), orientation)
    }

    /** Largest power-of-two subsampling that keeps the shorter side >= MIN_SHORT_SIDE. */
    fun sampleSizeFor(width: Int, height: Int): Int {
        var sample = 1
        while (minOf(width, height) / (sample * 2) >= MIN_SHORT_SIDE) sample *= 2
        return sample
    }

    /** CameraX frame to an upright bitmap. toBitmap() does not rotate, so it is done here. Closes the proxy. */
    fun fromImageProxy(image: ImageProxy): Bitmap = image.use {
        rotate(it.toBitmap().toArgb8888(), it.imageInfo.rotationDegrees.toFloat())
    }

    /** Small copy kept for the result screen, so the full photo can be released. */
    fun thumbnail(bitmap: Bitmap): Bitmap {
        val scale = THUMBNAIL_SIDE.toFloat() / maxOf(bitmap.width, bitmap.height)
        if (scale >= 1f) return bitmap
        return Bitmap.createScaledBitmap(bitmap, (bitmap.width * scale).toInt(), (bitmap.height * scale).toInt(), true)
    }

    private fun applyExifOrientation(bitmap: Bitmap, orientation: Int): Bitmap {
        val matrix = Matrix()
        when (orientation) {
            ExifInterface.ORIENTATION_ROTATE_90 -> matrix.postRotate(90f)
            ExifInterface.ORIENTATION_ROTATE_180 -> matrix.postRotate(180f)
            ExifInterface.ORIENTATION_ROTATE_270 -> matrix.postRotate(270f)
            ExifInterface.ORIENTATION_FLIP_HORIZONTAL -> matrix.postScale(-1f, 1f)
            ExifInterface.ORIENTATION_FLIP_VERTICAL -> matrix.postScale(1f, -1f)
            ExifInterface.ORIENTATION_TRANSPOSE -> { matrix.postRotate(90f); matrix.postScale(-1f, 1f) }
            ExifInterface.ORIENTATION_TRANSVERSE -> { matrix.postRotate(270f); matrix.postScale(-1f, 1f) }
            else -> return bitmap
        }
        return transform(bitmap, matrix)
    }

    private fun rotate(bitmap: Bitmap, degrees: Float): Bitmap =
        if (degrees == 0f) bitmap else transform(bitmap, Matrix().apply { postRotate(degrees) })

    private fun transform(bitmap: Bitmap, matrix: Matrix): Bitmap {
        val result = Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
        if (result !== bitmap) bitmap.recycle()
        return result
    }

    private fun Bitmap.toArgb8888(): Bitmap {
        if (config == Bitmap.Config.ARGB_8888) return this
        val converted = copy(Bitmap.Config.ARGB_8888, false)
        recycle()
        return converted
    }
}
