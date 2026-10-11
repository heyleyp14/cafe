package co.edu.unipamplona.cafedetector

import android.graphics.Color
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import co.edu.unipamplona.cafedetector.ui.CafeDetectorTheme
import co.edu.unipamplona.cafedetector.ui.CameraScreen
import co.edu.unipamplona.cafedetector.ui.ClassifierViewModel
import co.edu.unipamplona.cafedetector.ui.HomeScreen
import co.edu.unipamplona.cafedetector.ui.ResultScreen
import co.edu.unipamplona.cafedetector.ui.UiState

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // The theme is light-only: without this, a device in dark mode gets light icons on a light bar.
        val bars = SystemBarStyle.light(Color.TRANSPARENT, Color.TRANSPARENT)
        enableEdgeToEdge(statusBarStyle = bars, navigationBarStyle = bars)
        setContent { CafeDetectorTheme { CafeDetectorApp() } }
    }
}

private object Routes {
    const val HOME = "home"
    const val CAMERA = "camera"
    const val RESULT = "result"
}

/** [viewModel] is scoped to the Activity, so the three screens share it and it survives rotation. */
@Composable
private fun CafeDetectorApp(viewModel: ClassifierViewModel = viewModel()) {
    val navController = rememberNavController()
    val showResult = {
        navController.navigate(Routes.RESULT) {
            popUpTo(Routes.HOME)
            launchSingleTop = true
        }
    }
    val backHome: () -> Unit = { navController.popBackStack(Routes.HOME, inclusive = false) }

    NavHost(navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) {
            val modelVersion by viewModel.modelVersion.collectAsStateWithLifecycle()
            HomeScreen(
                modelVersion = modelVersion,
                onTakePhoto = { navController.navigate(Routes.CAMERA) { launchSingleTop = true } },
                onImagePicked = { uri ->
                    viewModel.classify(uri)
                    showResult()
                },
            )
        }
        composable(Routes.CAMERA) {
            CameraScreen(
                onBack = backHome,
                onCaptured = { image ->
                    viewModel.classify(image)
                    showResult()
                },
            )
        }
        composable(Routes.RESULT) {
            val state by viewModel.state.collectAsStateWithLifecycle()
            // After process death the back stack is restored but the result is gone.
            LaunchedEffect(state) { if (state is UiState.Idle) backHome() }
            ResultScreen(
                state = state,
                conditionFor = viewModel::conditionFor,
                onBack = backHome,
                onTakePhoto = {
                    navController.navigate(Routes.CAMERA) {
                        popUpTo(Routes.HOME)
                        launchSingleTop = true
                    }
                },
                // Stays on this screen: the state goes back to loading and then to the new result.
                onImagePicked = viewModel::classify,
            )
        }
    }
}
