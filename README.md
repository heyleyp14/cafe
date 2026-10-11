# Detector de plagas y enfermedades en hojas de café (prototipo)

Prototipo académico de apoyo, **no es una herramienta de diagnóstico**. Clasifica una foto de una hoja de café en `minador`, `roya` o `sana` con un modelo EfficientNet-B0 que corre en el teléfono, sin internet.

Proyecto "Sistema de Detección Temprana de Plagas y Enfermedades en Cultivos de Café" (FCPD 2026-2, Universidad de Pamplona). El plan está en `PLAN_Prototipo_Cafe_Kotlin.md`.

## Documentos

| Archivo | Contenido |
|---|---|
| `docs/resultados.md` | Métricas, umbral, paridad, latencia y limitaciones (generado, no editar) |
| `docs/bitacora.md` | Qué se hizo, qué se comprobó y qué no se ejecutó en cada fase |
| `docs/decisiones.md` | Decisiones tomadas y su motivo |
| `docs/MANUAL_WINDOWS.md` | Instalación paso a paso en Windows (sin probar en Windows) |

## Requisitos

- Python 3.10 a 3.13 (TensorFlow 2.21.0 no admite 3.14) y `uv`.
- Android SDK con una plataforma instalada, `adb` y JDK 17 o superior.
- Para entrenar: Google Colab o Kaggle con GPU.

## Reproducir el modelo

### 1. Entorno local

```bash
uv venv --python 3.12 ml/.venv
uv pip install --python ml/.venv/bin/python -r ml/requirements.txt
```

### 2. Datos

Descarga RoCoLe y DECAFIA (enlaces abajo) en `ml/data/raw/rocole/` y `ml/data/raw/decafia/`, descomprímelos y ejecuta:

```bash
make data        # particiones 70/15/15 y ml/outputs/dataset_stats.json
```

### 3. Entrenamiento y evaluación en Colab

El modelo actual (v2, EfficientNet-B0) se entrena en Colab con GPU. El plan y sus motivos están en `docs/PLAN_reentrenamiento_v2.md`.

```bash
make data                      # incluye BRACOL en ml/data/external/bracol (ver docs/decisiones.md)
make colab-bundle colab-data   # cafe_ml_bundle.zip (código) y cafe_data_v2.zip (datos preparados)
```

Sube los dos zip a `/content/` de una sesión de Colab con GPU, descomprímelos y ejecuta desde `/content/ml`:

```bash
python colab_run_v2.py                                # etapa 1: compara arquitecturas sin BRACOL
python colab_run_v2.py --stage 2 --arch efficientnetb0  # etapa 2: modelo final
```

Descarga `cafe_outputs_v2.zip` y copia `outputs/final/` a `ml/outputs/final/`.

### 4. Conversión, paridad y archivos para la app

```bash
make tflite parity             # ml/outputs/final/: modelos TFLite, parity.json y golden/
cp ml/outputs/final/model_fp32.tflite android/app/src/main/assets/model.tflite
cp ml/outputs/final/labels.txt ml/outputs/final/threshold.json android/app/src/main/assets/
cp ml/outputs/final/golden/* android/app/src/androidTest/assets/golden/
make results                   # regenera docs/resultados.md
```

La app usa el modelo sin cuantizar y un umbral elegido con una fuente no vista; los motivos están en `docs/decisiones.md`. El conjunto final (JMuBEN) se evalúa una sola vez con `ml/evaluar_conjunto_final.py`.

## Compilar y probar la app

```bash
cd android
echo "sdk.dir=$HOME/Android/Sdk" > local.properties
./gradlew testDebugUnitTest assembleDebug          # pruebas unitarias y APK
./gradlew connectedDebugAndroidTest                # pruebas instrumentadas (emulador x86_64 o teléfono)
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Las imágenes de referencia (`golden/*.jpg`, `golden/*.rgb`) no están en git; se regeneran con `make parity` (necesita `ml/outputs/final/model.keras`).

## Datasets

Las imágenes no se incluyen en este repositorio.

- **RoCoLe.** Parraga-Alava, J., Cusme, K., Loor, A., Santander, E. (2019). *RoCoLe: A robusta coffee leaf images dataset*. Mendeley Data, v2. https://doi.org/10.17632/c5yvn32dzg.2 — CC BY 4.0.
- **DECAFIA (CoffeeLeaf-CO).** Rosas Ruiz, L. E., Salom Medina, A. F., Barrero Perez, J. G. (2026). *DECAFIA: A Field-Collected Coffee Leaf Disease Detection Dataset from Santander, Colombia*. Zenodo. https://doi.org/10.5281/zenodo.19931904 — CC BY 4.0.
- DECAFIA incluye imágenes de: Silva, L. B. et al. (2020). *Rust and leaf miner in coffee crop (Coffea arabica)*. Mendeley Data. https://doi.org/10.17632/vfxf4trtcg.5 — CC BY 4.0.

Licencia CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
