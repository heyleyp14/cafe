package co.edu.unipamplona.cafedetector.ui

import android.graphics.Bitmap
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts.PickVisualMedia
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import co.edu.unipamplona.cafedetector.R
import co.edu.unipamplona.cafedetector.data.Condition
import co.edu.unipamplona.cafedetector.ml.ClassificationResult

private val CAPTURE_TIPS = listOf(
    R.string.result_tip_close,
    R.string.result_tip_light,
    R.string.result_tip_background,
    R.string.result_tip_steady,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultScreen(
    state: UiState,
    conditionFor: (String) -> Condition?,
    onBack: () -> Unit,
    onTakePhoto: () -> Unit,
    onImagePicked: (Uri) -> Unit,
) {
    val picker = rememberLauncherForActivityResult(PickVisualMedia()) { uri -> uri?.let(onImagePicked) }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.result_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(painterResource(R.drawable.ic_arrow_back), contentDescription = stringResource(R.string.action_back))
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background),
            )
        },
        bottomBar = {
            if (state is UiState.Success || state is UiState.Error) {
                // Same two ways to bring a new image as the home screen.
                Row(
                    modifier = Modifier
                        .navigationBarsPadding()
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Button(onClick = onTakePhoto, modifier = Modifier.weight(1f).heightIn(min = 52.dp)) {
                        Text(stringResource(R.string.result_take_photo), textAlign = TextAlign.Center)
                    }
                    FilledTonalButton(
                        onClick = { picker.launch(PickVisualMediaRequest(PickVisualMedia.ImageOnly)) },
                        modifier = Modifier.weight(1f).heightIn(min = 52.dp),
                    ) {
                        Text(stringResource(R.string.result_pick_gallery), textAlign = TextAlign.Center)
                    }
                }
            }
        },
    ) { padding ->
        val modifier = Modifier.fillMaxSize().padding(padding)
        when (state) {
            is UiState.Success ->
                if (state.result.accepted) {
                    AcceptedResult(state.result, state.bitmap, conditionFor, modifier)
                } else {
                    UncertainResult(state.result, state.bitmap, modifier)
                }
            is UiState.Error -> MessagePanel(
                title = stringResource(R.string.result_error_title),
                message = stringResource(state.message),
                modifier = modifier,
                secondaryAction = stringResource(R.string.action_back_home) to onBack,
            )
            // Idle only shows for the frame before the host navigates away from this screen.
            UiState.Loading, UiState.Idle -> LoadingPanel(modifier)
        }
    }
}

@Composable
private fun LoadingPanel(modifier: Modifier) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        CircularProgressIndicator()
        Text(stringResource(R.string.result_loading), style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable
private fun AcceptedResult(
    result: ClassificationResult,
    thumbnail: Bitmap,
    conditionFor: (String) -> Condition?,
    modifier: Modifier,
) {
    val best = result.top.first()
    val condition = conditionFor(best.label)
    val percent = confidencePercent(best.confidence)

    Column(
        modifier = modifier.verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp),
    ) {
        SectionCard {
            Row(Modifier.padding(16.dp), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Thumbnail(thumbnail, Modifier.size(96.dp))
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        text = stringResource(R.string.result_detected_class),
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Text(
                        text = condition?.nombre ?: best.label,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.semantics { heading() },
                    )
                    val confidenceDescription = stringResource(R.string.result_confidence_description, percent)
                    // Read as one phrase instead of "Confianza", "87 %" and an unlabeled progress bar.
                    Column(
                        modifier = Modifier.padding(top = 4.dp)
                            .clearAndSetSemantics { contentDescription = confidenceDescription },
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(
                                text = stringResource(R.string.result_confidence),
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Text(
                                text = stringResource(R.string.percent_value, percent),
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                            )
                        }
                        ConfidenceBar(best.confidence)
                    }
                }
            }
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionLabel(stringResource(R.string.result_top_title))
            SectionCard {
                result.top.forEachIndexed { index, prediction ->
                    if (index > 0) HorizontalDivider(Modifier.padding(start = 16.dp))
                    Column(
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Text(
                                text = conditionFor(prediction.label)?.nombre ?: prediction.label,
                                style = MaterialTheme.typography.bodyLarge,
                                modifier = Modifier.weight(1f),
                            )
                            Text(
                                text = stringResource(R.string.percent_value, confidencePercent(prediction.confidence)),
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        ConfidenceBar(prediction.confidence, Modifier.clearAndSetSemantics { })
                    }
                }
            }
        }

        if (condition != null) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                SectionLabel(stringResource(R.string.result_sheet_title))
                SectionCard {
                    SheetSection(stringResource(R.string.result_symptoms), condition.sintomas)
                    if (condition.condiciones.isNotBlank()) {
                        HorizontalDivider(Modifier.padding(start = 16.dp))
                        SheetSection(stringResource(R.string.result_favorable_conditions), condition.condiciones)
                    }
                }
            }
        }
        SupportNotice()
    }
}

@Composable
private fun UncertainResult(result: ClassificationResult, thumbnail: Bitmap, modifier: Modifier) {
    Column(
        modifier = modifier.verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Thumbnail(thumbnail, Modifier.size(120.dp))
            Text(
                text = stringResource(R.string.result_uncertain_title),
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center,
                modifier = Modifier.semantics { heading() },
            )
            Text(
                text = stringResource(
                    R.string.result_uncertain_message,
                    confidencePercent(result.top.first().confidence),
                ),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SectionLabel(stringResource(R.string.result_tips_title))
            SectionCard {
                CAPTURE_TIPS.forEachIndexed { index, tip ->
                    if (index > 0) HorizontalDivider(Modifier.padding(start = 16.dp))
                    Text(
                        text = stringResource(tip),
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                    )
                }
            }
        }
        SupportNotice()
    }
}

@Composable
private fun Thumbnail(bitmap: Bitmap, modifier: Modifier) {
    Image(
        bitmap = bitmap.asImageBitmap(),
        contentDescription = stringResource(R.string.result_thumbnail_description),
        contentScale = ContentScale.Crop,
        modifier = modifier.clip(MaterialTheme.shapes.medium),
    )
}

@Composable
private fun ConfidenceBar(confidence: Float, modifier: Modifier = Modifier) {
    LinearProgressIndicator(
        progress = { confidence.coerceIn(0f, 1f) },
        modifier = modifier.fillMaxWidth(),
        trackColor = MaterialTheme.colorScheme.surfaceVariant,
        gapSize = 0.dp,
        drawStopIndicator = {},
    )
}

@Composable
private fun SheetSection(title: String, body: String) {
    Column(
        modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(title, style = MaterialTheme.typography.titleMedium, modifier = Modifier.semantics { heading() })
        Text(body, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
