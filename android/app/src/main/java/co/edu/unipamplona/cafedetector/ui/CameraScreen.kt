package co.edu.unipamplona.cafedetector.ui

import android.Manifest
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import android.util.Log
import android.util.Size
import androidx.activity.compose.LocalActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts.RequestPermission
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import androidx.lifecycle.compose.LocalLifecycleOwner
import co.edu.unipamplona.cafedetector.R

private const val TAG = "CameraScreen"

// The model sees 224x224, so a full-sensor capture would only cost memory and decode time.
private val CAPTURE_SIZE = Size(1280, 960)
private val Scrim = Color.Black.copy(alpha = 0.55f)

/** [onCaptured] receives ownership of the frame and must close it. */
@Composable
fun CameraScreen(onBack: () -> Unit, onCaptured: (ImageProxy) -> Unit) {
    val context = LocalContext.current
    var granted by remember { mutableStateOf(context.hasCameraPermission()) }
    var asked by rememberSaveable { mutableStateOf(false) }
    var answered by rememberSaveable { mutableStateOf(false) }
    val permissionLauncher = rememberLauncherForActivityResult(RequestPermission()) {
        granted = it
        answered = true
    }

    LaunchedEffect(Unit) {
        if (!granted && !asked) {
            asked = true
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }
    // The user may grant the permission in the system settings and come back.
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { granted = context.hasCameraPermission() }

    var cameraFailed by remember { mutableStateOf(false) }
    when {
        cameraFailed -> Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            MessagePanel(
                title = stringResource(R.string.camera_unavailable_title),
                message = stringResource(R.string.camera_unavailable_message),
                modifier = Modifier.safeDrawingPadding(),
                secondaryAction = stringResource(R.string.action_back_home) to onBack,
            )
        }
        granted -> CameraPreview(onBack, onCaptured, onCameraFailed = { cameraFailed = true })
        answered -> Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            MessagePanel(
                title = stringResource(R.string.camera_denied_title),
                message = stringResource(R.string.camera_denied_message),
                modifier = Modifier.safeDrawingPadding(),
                primaryAction = stringResource(R.string.camera_open_settings) to { context.openAppSettings() },
                secondaryAction = stringResource(R.string.action_back_home) to onBack,
            )
        }
        // The system permission dialog is on top; nothing to show behind it yet.
        else -> Box(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background))
    }
}

@Composable
private fun CameraPreview(onBack: () -> Unit, onCaptured: (ImageProxy) -> Unit, onCameraFailed: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember { PreviewView(context) }
    val imageCapture = remember {
        ImageCapture.Builder()
            .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
            .setResolutionSelector(
                ResolutionSelector.Builder()
                    .setResolutionStrategy(
                        ResolutionStrategy(CAPTURE_SIZE, ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER),
                    )
                    .build(),
            )
            .build()
    }
    var capturing by remember { mutableStateOf(false) }
    var captureFailed by remember { mutableStateOf(false) }

    DisposableEffect(lifecycleOwner) {
        var disposed = false
        val providerFuture = ProcessCameraProvider.getInstance(context)
        providerFuture.addListener({
            if (disposed) return@addListener
            try {
                val provider = providerFuture.get()
                val selector = listOf(CameraSelector.DEFAULT_BACK_CAMERA, CameraSelector.DEFAULT_FRONT_CAMERA)
                    .first { provider.hasCamera(it) } // throws when the device has no camera at all
                val preview = Preview.Builder().build().apply { setSurfaceProvider(previewView.surfaceProvider) }
                provider.unbindAll()
                provider.bindToLifecycle(lifecycleOwner, selector, preview, imageCapture)
            } catch (e: Exception) {
                Log.e(TAG, "Camera could not be started", e)
                onCameraFailed()
            }
        }, ContextCompat.getMainExecutor(context))
        onDispose {
            disposed = true
            if (providerFuture.isDone) runCatching { providerFuture.get().unbindAll() }
        }
    }

    DarkSystemBars()

    Box(Modifier.fillMaxSize().background(Color.Black)) {
        val previewDescription = stringResource(R.string.camera_preview_description)
        AndroidView(
            factory = { previewView },
            modifier = Modifier.fillMaxSize().semantics { contentDescription = previewDescription },
        )

        Column(
            modifier = Modifier.fillMaxSize().safeDrawingPadding(),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            TextButton(
                onClick = onBack,
                colors = ButtonDefaults.textButtonColors(containerColor = Scrim, contentColor = Color.White),
                modifier = Modifier.align(Alignment.Start).padding(12.dp),
            ) {
                Text(stringResource(R.string.camera_cancel))
            }

            Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
                LeafGuideFrame(Modifier.padding(24.dp).widthIn(max = 280.dp).aspectRatio(3f / 4f))
            }

            Column(
                modifier = Modifier.fillMaxWidth().background(Scrim).padding(vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = stringResource(
                        if (captureFailed) R.string.camera_capture_error else R.string.camera_frame_hint,
                    ),
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 24.dp),
                )
                CaptureButton(enabled = !capturing) {
                    capturing = true
                    captureFailed = false
                    imageCapture.takePicture(
                        ContextCompat.getMainExecutor(context),
                        object : ImageCapture.OnImageCapturedCallback() {
                            override fun onCaptureSuccess(image: ImageProxy) = onCaptured(image)

                            override fun onError(exception: ImageCaptureException) {
                                Log.e(TAG, "Capture failed", exception)
                                capturing = false
                                captureFailed = true
                            }
                        },
                    )
                }
            }
        }
    }
}

/** Four corner brackets, as in the mockup, so the leaf itself stays unobstructed. */
@Composable
private fun LeafGuideFrame(modifier: Modifier) {
    Canvas(modifier) {
        val arm = 32.dp.toPx()
        val stroke = 3.dp.toPx()
        val (w, h) = size
        fun corner(x: Float, y: Float, dx: Float, dy: Float) {
            drawLine(Color.White, Offset(x, y), Offset(x + dx, y), stroke, StrokeCap.Round)
            drawLine(Color.White, Offset(x, y), Offset(x, y + dy), stroke, StrokeCap.Round)
        }
        corner(0f, 0f, arm, arm)
        corner(w, 0f, -arm, arm)
        corner(0f, h, arm, -arm)
        corner(w, h, -arm, -arm)
    }
}

@Composable
private fun CaptureButton(enabled: Boolean, onClick: () -> Unit) {
    val description = stringResource(R.string.camera_capture)
    Box(
        modifier = Modifier
            .size(72.dp)
            .border(3.dp, Color.White, CircleShape)
            .clickable(enabled = enabled, role = Role.Button, onClick = onClick)
            .semantics { contentDescription = description },
        contentAlignment = Alignment.Center,
    ) {
        Box(Modifier.size(58.dp).background(if (enabled) Color.White else Color.Gray, CircleShape))
    }
}

/** The app theme is light, so the status bar icons are dark; over the black preview they must be light. */
@Composable
private fun DarkSystemBars() {
    val window = LocalActivity.current?.window ?: return
    DisposableEffect(window) {
        val controller = WindowCompat.getInsetsController(window, window.decorView)
        controller.isAppearanceLightStatusBars = false
        controller.isAppearanceLightNavigationBars = false
        onDispose {
            controller.isAppearanceLightStatusBars = true
            controller.isAppearanceLightNavigationBars = true
        }
    }
}

private fun Context.hasCameraPermission(): Boolean =
    ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED

private fun Context.openAppSettings() {
    val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.fromParts("package", packageName, null))
    try {
        startActivity(intent)
    } catch (e: ActivityNotFoundException) {
        Log.e(TAG, "App settings screen is not available", e)
    }
}
