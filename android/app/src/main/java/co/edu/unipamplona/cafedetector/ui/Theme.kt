package co.edu.unipamplona.cafedetector.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Palette of the v0 mockup. Its green tint (#34C759-like) only reaches about 2:1 against white,
// so primary uses a darker green of the same hue to keep text and buttons above WCAG AA (4.5:1).
private val Green = Color(0xFF1B6E3A)
private val GreenContainer = Color(0xFFDDF3E2)
private val OnGreenContainer = Color(0xFF14432A)
private val GroupedBackground = Color(0xFFF2F2F7)
private val Label = Color(0xFF1A1A1C)
private val SecondaryLabel = Color(0xFF55555C)
private val WarningContainer = Color(0xFFFBF0D9)
private val OnWarningContainer = Color(0xFF6B3F0C)

private val LightColors = lightColorScheme(
    primary = Green,
    onPrimary = Color.White,
    primaryContainer = GreenContainer,
    onPrimaryContainer = OnGreenContainer,
    secondary = Green,
    onSecondary = Color.White,
    secondaryContainer = GreenContainer,
    onSecondaryContainer = OnGreenContainer,
    tertiary = OnWarningContainer,
    onTertiary = Color.White,
    tertiaryContainer = WarningContainer,
    onTertiaryContainer = OnWarningContainer,
    background = GroupedBackground,
    onBackground = Label,
    surface = Color.White,
    onSurface = Label,
    surfaceVariant = Color(0xFFE5E5EA),
    onSurfaceVariant = SecondaryLabel,
    surfaceContainerLowest = Color.White,
    surfaceContainerLow = Color.White,
    surfaceContainer = Color(0xFFF7F7FA),
    surfaceContainerHigh = Color(0xFFF2F2F7),
    surfaceContainerHighest = Color(0xFFE5E5EA),
    outline = Color(0xFF8E8E96),
    outlineVariant = Color(0xFFD1D1D6),
    error = Color(0xFFB3261E),
    onError = Color.White,
    errorContainer = Color(0xFFF9DEDC),
    onErrorContainer = Color(0xFF601410),
)

@Composable
fun CafeDetectorTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = LightColors, content = content)
}
