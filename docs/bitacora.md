# Bitácora

## Fase 0 — Preparación del entorno (2026-10-10)

**Estado: CERRADA.** Criterios de aceptación cumplidos: estructura creada, entorno comprobado, licencias anotadas. (Estuvo bloqueada en el paso 2 hasta que el humano instaló `uv`.)

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

### Actualización: paso 2 desbloqueado (2026-10-10)

- El humano instaló `uv 0.13.0`. Se creó `ml/.venv` con CPython 3.12.8 (`uv venv --python 3.12 ml/.venv`).
- Instalación verificada y versiones fijadas en `ml/requirements.txt`: tensorflow 2.21.0, keras 3.15.1, numpy 2.5.4, scikit-learn 1.9.1, matplotlib 3.11.2, pillow 12.3.0.
- Prueba de conversión TFLite ejecutada con un MobileNetV2 **sin pesos entrenados** (solo comprueba que la conversión funciona, no mide calidad): los dos archivos (fp32 y rango dinámico) se generan con entrada `[1,224,224,3] float32` y salida `[1,3] float32`, como exige el contrato de la sección 4.
- `tf.lite.Interpreter` emite un aviso de obsolescencia que recomienda `ai_edge_litert`; sigue funcionando en 2.21.0 y es la API que indica el plan.
- **GPU: NO DISPONIBLE.** TensorFlow no detecta GPU (`list_physical_devices("GPU")` devuelve vacío) y `nvidia-smi` sigue fallando por el desajuste del controlador. El entrenamiento se hará en CPU (16 hilos, 23 GB de RAM) salvo que se corrija; el plan lo permite ("también corre en CPU, más lento").
- `Makefile` usa ahora `ml/.venv/bin/python` por defecto.

Las entradas "NO EJECUTADO" de arriba sobre instalación y conversión quedan resueltas. Siguen pendientes: Android SDK y `adb` (fase 6) y el informe del proyecto (fase 7).

### Actualización: GPU habilitada (2026-10-10)

- El humano reinició el equipo; el módulo del kernel y `nvidia-utils` coinciden ahora en 615.78.08 y `nvidia-smi` reporta "NVIDIA GeForce RTX 4050 Laptop GPU", 6141 MiB.
- Se instaló `tensorflow[and-cuda]==2.21.0` en `ml/.venv` (añade los paquetes `nvidia-*-cu12`).
- Tras instalar, TensorFlow seguía sin ver la GPU ("Cannot dlopen some GPU libraries"). Causa: no encuentra las librerías CUDA que pip deja dentro del entorno. Solución: añadir las carpetas `site-packages/nvidia/*/lib` a `LD_LIBRARY_PATH`; el `Makefile` lo hace automáticamente.
- Comprobado: con esa variable, `list_physical_devices("GPU")` devuelve la RTX 4050 y una pasada de MobileNetV2 se ejecuta en `GPU:0`.
- Queda sin efecto la nota anterior "GPU: NO DISPONIBLE". Ejecutar los scripts con `make` (o exportando la variable) para usar la GPU.
