package co.edu.unipamplona.cafedetector.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts.PickVisualMedia
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import co.edu.unipamplona.cafedetector.R

private val TIPS = listOf(
    R.string.home_tip_single_leaf,
    R.string.home_tip_light,
    R.string.home_tip_focus,
    R.string.home_tip_background,
)

@Composable
fun HomeScreen(
    modelVersion: String?,
    onTakePhoto: () -> Unit,
    onImagePicked: (Uri) -> Unit,
) {
    var aboutOpen by rememberSaveable { mutableStateOf(false) }
    // The system photo picker grants access to the chosen image only, so no storage permission is needed.
    val picker = rememberLauncherForActivityResult(PickVisualMedia()) { uri -> uri?.let(onImagePicked) }

    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 24.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = stringResource(R.string.app_name),
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.semantics { heading() },
                )
                Text(
                    text = stringResource(R.string.home_subtitle),
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                SectionLabel(stringResource(R.string.home_instructions_title))
                SectionCard {
                    TIPS.forEachIndexed { index, tip ->
                        if (index > 0) HorizontalDivider(Modifier.padding(start = 44.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp).padding(horizontal = 16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(16.dp),
                        ) {
                            Box(Modifier.size(12.dp).background(MaterialTheme.colorScheme.primary, CircleShape))
                            Text(stringResource(tip), style = MaterialTheme.typography.bodyLarge)
                        }
                    }
                }
            }

            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(onClick = onTakePhoto, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) {
                    Text(stringResource(R.string.home_take_photo))
                }
                FilledTonalButton(
                    onClick = { picker.launch(PickVisualMediaRequest(PickVisualMedia.ImageOnly)) },
                    modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp),
                ) {
                    Text(stringResource(R.string.home_pick_gallery))
                }
            }

            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                SupportNotice()
                TextButton(onClick = { aboutOpen = true }, modifier = Modifier.padding(horizontal = 4.dp)) {
                    Text(stringResource(R.string.home_about))
                }
            }
        }
    }

    if (aboutOpen) AboutDialog(modelVersion, onDismiss = { aboutOpen = false })
}

@Composable
private fun AboutDialog(modelVersion: String?, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { TextButton(onClick = onDismiss) { Text(stringResource(R.string.action_close)) } },
        title = { Text(stringResource(R.string.about_title)) },
        text = {
            Column(
                modifier = Modifier.verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                AboutHeading(stringResource(R.string.about_model_title))
                Text(
                    stringResource(
                        R.string.about_model_version,
                        modelVersion ?: stringResource(R.string.about_model_version_unavailable),
                    ),
                )
                AboutHeading(stringResource(R.string.about_datasets_title), Modifier.padding(top = 8.dp))
                Text(stringResource(R.string.about_dataset_rocole))
                Text(stringResource(R.string.about_dataset_decafia))
                Text(stringResource(R.string.about_dataset_silva))
                Text(
                    text = stringResource(R.string.support_tool_notice),
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 8.dp),
                )
            }
        },
    )
}

@Composable
private fun AboutHeading(text: String, modifier: Modifier = Modifier) {
    Text(
        text = text,
        style = MaterialTheme.typography.titleSmall,
        color = MaterialTheme.colorScheme.onSurface,
        modifier = modifier.semantics { heading() },
    )
}
