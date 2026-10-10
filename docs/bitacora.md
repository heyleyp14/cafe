# Bitácora

## Fase 0 — Preparación del entorno (2026-10-10)

**Estado: BLOQUEADA en el paso 2** (falta un Python compatible con TensorFlow). Los pasos 1, 3, 4 y 5 están hechos.

### Qué se hizo

- Estructura de la sección 3 creada, `git init` (rama `main`) y `.gitignore`.
- `ml/config.py` con `CLASSES = ["minador", "roya", "sana"]`, `IMG_SIZE = 224`, `SEED = 42` y rutas.
- `Makefile` con los atajos `data train eval tflite parity` (los scripts aún no existen; se crean en las fases 1–5).
- `docs/decisiones.md` con licencias, raíz del repositorio, alcance de la v1 y significado de "coco".
- `README.md` inicial con las citas de los datasets.

### Qué se comprobó

| Herramienta | Requerido | Encontrado | Estado |
|---|---|---|---|
| Python | 3.10+ con wheel de TensorFlow | 3.14.8 (único intérprete instalado) | **FALTA**: `tensorflow 2.21.0` solo publica wheels cp310–cp313 |
| pip | sí | `/usr/bin/pip` | OK |
| Gestor de versiones de Python | — | no hay `uv`, `pyenv`, `conda` | Falta (`uv 0.13.0` está disponible en el repositorio `extra` de pacman) |
| JDK | 17 | OpenJDK 21.0.12 (único instalado) | Distinto al indicado; se validará en la fase 6 |
| Android SDK | sí | no hay `ANDROID_HOME`, `~/Android/Sdk`, `sdkmanager` ni `aapt` | **FALTA** (necesario desde la fase 6) |
| adb | si se prueba en dispositivo | no instalado | **FALTA** (necesario en fases 9–12) |
| GPU | recomendada | RTX 4050 presente, pero `nvidia-smi` falla: "Driver/library version mismatch" (módulo del kernel 615.71.09, `nvidia-utils` 615.78.08) | **No usable ahora**; normalmente se corrige reiniciando |
| Docker | — | instalado, demonio detenido | No usable ahora |
| Red | PyPI, Maven Central, Google Maven | las tres responden HTTP 200 | OK |
| git, make, gradle | sí | instalados | OK |

- Versiones consultadas en PyPI el 2026-10-10: tensorflow 2.21.0, numpy 2.5.4, scikit-learn 1.9.1, matplotlib 3.11.2, Pillow 12.3.0.
- Licencias leídas en la fuente: RoCoLe (API de Mendeley Data) y DECAFIA (API de Zenodo), ambas CC BY 4.0 y de acceso abierto.
- "coco" en DECAFIA = defoliación por gorgojos (Curculionidae); no entra en la v1.

### NO EJECUTADO

- **Instalación de `ml/requirements.txt` y prueba de conversión TFLite:** NO EJECUTADO. No hay intérprete Python 3.10–3.13. Las versiones del archivo existen en PyPI pero no están verificadas instaladas.
- **Comprobación de GPU con TensorFlow:** NO EJECUTADO, por el mismo motivo y por el desajuste del controlador NVIDIA.

### Pendiente

- Decisión del humano sobre cómo obtener Python 3.12 (ver resumen de la fase).
- Android SDK + `adb` antes de la fase 6.
- Hallazgos que afectan la fase 1: DECAFIA contiene hojas sanas de RoCoLe (`SANAS_ROCOLE_*`) e imágenes de Silva et al. (`MINEIRO_*`); hay que deduplicar entre datasets antes de dividir.
