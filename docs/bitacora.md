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

## Fase 1 — Datos (2026-10-10)

**Estado: CERRADA.** Criterios de aceptación cumplidos (detalle abajo). Todas las cifras salen de `ml/outputs/dataset_stats.json`.

### Qué se hizo

- Descarga de RoCoLe (Mendeley, 1560 imágenes) y DECAFIA (Zenodo) a `ml/data/raw/` (fuera de git).
- `ml/01_preparar_datos.py`: etiquetas a nivel de imagen, exclusiones, deduplicación, división 70/15/15 por grupos y `dataset_stats.json`. Se ejecuta con `make data` (unos 10 s).
- Hojas de contacto para la revisión manual en `ml/data/review/` (fuera de git).

### Hallazgos sobre los datos

- **DECAFIA trae 2769 imágenes, no las 2786 que anuncia** su descripción (su propia partición suma 1934 + 549 + 286 = 2769).
- "coco" = defoliación por gorgojos; no se usa.
- Hay muchas copias: 535 duplicados eliminados (61 de ellos entre los dos datasets) y 11 imágenes descartadas por ser copias con etiquetas contradictorias. `SANAS_NUEVAS_*` contiene copias rotadas de `SANAS_SOCORRO_*`, y RoCoLe repite fotos bajo identificadores de planta distintos.
- Algunas imágenes `ROYA_*` de DECAFIA son copias de RoCoLe, aunque su documentación dice que solo reutilizó hojas sanas.

### Descartes (por regla)

| Regla | Imágenes |
|---|---|
| DECAFIA `SANAS_ROCOLE_*` (derivadas de RoCoLe) | 454 |
| DECAFIA con clase dominante `coco` | 426 |
| RoCoLe arañita roja | 167 |
| Duplicados eliminados | 535 |
| Copias con etiquetas contradictorias | 11 |
| Empates de clase dominante | 0 |

### Resultado: 2736 imágenes

| Clase | train | val | test | Total | Origen |
|---|---|---|---|---|---|
| minador | 260 | 56 | 56 | 372 | DECAFIA 372 |
| roya | 636 | 136 | 136 | 908 | RoCoLe 568, DECAFIA 340 |
| sana | 1019 | 219 | 218 | 1456 | RoCoLe 745, DECAFIA 711 |

### Qué se comprobó (criterios de aceptación)

- **Ninguna imagen en dos particiones:** 0 coincidencias por MD5, 0 pares con distancia perceptual ≤ 52 entre particiones y 0 grupos repartidos. Verificado además con un cálculo independiente sobre los archivos ya copiados: la distancia mínima entre particiones es 53.
- **≥ 100 imágenes de entrenamiento por clase:** sí; la menor es `minador` con 260.
- **Desbalance reportado:** razón clase mayor/menor en train = 3.919 (`sana`/`minador`). La fase 2 debe usar `class_weight`.
- Fracciones reales por clase: entre 0.6989 y 0.7004 en train; entre 0.1497 y 0.1505 en val y test.

### Revisión manual de etiquetas (20 imágenes por clase)

Hecha por el agente mirando miniaturas, **no por una persona experta en café**:

- `minador`: las 20 muestran lesiones coherentes con minador.
- `sana`: en ninguna de las 20 se aprecian lesiones.
- `roya`: ninguna etiqueta absurda, pero en varias de RoCoLe (roya nivel 1) las lesiones son tan pequeñas que a tamaño de miniatura no se distinguen de una hoja sana. No se pudo confirmar ni descartar ruido de etiquetas en esos casos.

### Limitaciones que hay que llevar al informe

- **Sesgo de fondo en `minador`:** 19 de las 20 imágenes revisadas son hojas sobre fondo blanco o de laboratorio, mientras que casi todas las de `sana` son fotos de campo. El modelo puede aprender "fondo blanco = minador". Hay que comprobarlo en la fase 12 con fotos reales.
- **`minador` es pequeña** (56 imágenes de test): sus métricas tendrán intervalos amplios.
- **Fuga residual no eliminada en `sana`:** DECAFIA contiene varias tomas distintas de una misma hoja (otra posición, otro encuadre) y no trae metadatos para agruparlas. El hash no las une porque no son la misma foto. Entre las series `SANAS_NUEVAS_*` y `SANAS_SOCORRO_*` quedan 26 pares en particiones distintas con distancia 53–64; al mirarlos, varios son la misma hoja fotografiada dos veces. Puede inflar un poco las métricas de `sana` en test. En `minador` y `roya` los pares revisados con distancia > 52 eran hojas distintas sobre fondo blanco.
- Dominio: RoCoLe es Robusta (Ecuador) y las imágenes `MINEIRO_*` son de Brasil.

### Corrección por instrucción del humano (2026-10-10)

El humano indicó ceñirse totalmente al plan. Cambios:

- **Se revirtió la exclusión de recortes de lesión** (`*_RECORTE(S)_*`), que era una regla propia y no del plan. Las cifras de esta sección ya son las de la ejecución sin esa exclusión. La revisión manual y el recuento independiente de arriba se hicieron con la versión anterior (2519 imágenes); la comprobación de fugas integrada en el script se repitió y sigue en 0/0/0.
- **Riesgo que se asume al incluirlos:** un recorte puede provenir de una foto que quedó en otra partición, y un hash no lo detecta. Además son acercamientos, distintos de la hoja completa que recibirá la app.
- **El entrenamiento (fase 2) se hará en Google Colab o Kaggle**, como indica el plan. La GPU local queda solo para pruebas de humo de los scripts; ninguna cifra del informe saldrá de ella.

### NO EJECUTADO

- Revisión manual de una muestra de los recortes reincorporados.
- Revisión de etiquetas por una persona experta. Las hojas de contacto están en `ml/data/review/` para quien quiera hacerla.

## Fases 2 a 5 — Scripts listos, ejecución pendiente en la nube (2026-10-10)

**Estado: NINGUNA de estas fases está cerrada.** Los criterios de aceptación se verifican con la ejecución en Colab o Kaggle, que todavía no se ha hecho.

### Qué se hizo

- `ml/02_entrenar.py`, `ml/03_evaluar.py`, `ml/04_convertir_tflite.py`, `ml/05_paridad_tflite.py`.
- `ml/colab_entrenamiento.ipynb`: ejecuta las fases 1 a 5 en orden; al final de cada fase comprueba sus criterios de aceptación y se detiene si no se cumplen.
- `make colab-bundle` genera `cafe_ml_bundle.zip` (solo código) para subirlo al cuaderno.
- `MODEL_VERSION = "v1-2026-10"` en `ml/config.py`.

### Qué se comprobó

- Prueba de humo local de la cadena completa (fases 2 a 5) con **una sola época por etapa**, únicamente para confirmar que los scripts corren y producen todos los archivos con el formato esperado: los 4 scripts terminan sin error, `model_io.json` cumple el contrato de la sección 4 y cada `NN.rgb` pesa 150528 bytes (224·224·3).
- Los archivos de esa prueba **se borraron**: no son resultados y ninguna cifra suya se usa en el proyecto.
- Nota de transparencia: la prueba de humo evaluó sobre test con un modelo de una época. No se usó para decidir nada (ni hiperparámetros ni umbral).

### NO EJECUTADO

- **Entrenamiento real (fase 2), evaluación (3), conversión (4) y paridad (5):** pendientes de ejecutar en Colab o Kaggle por el humano.
- **El cuaderno no se ha probado en Colab ni en Kaggle** (no hay acceso desde aquí). En particular no está verificado que `tensorflow[and-cuda]==2.21.0` detecte la GPU allí; la primera celda de comprobación falla con un mensaje claro si no la ve.
- Comparación opcional con EfficientNet-B0 y ResNet50: no implementada.

## Fases 2 a 5 — Ejecución en Google Colab (2026-10-10)

**Estado: fases 2, 3, 4 y 5 CERRADAS.** Todas las cifras salen de los archivos de `ml/outputs/` generados en Colab; no hay ninguna cifra de la GPU local.

### Cómo se ejecutó

- Google Colab, GPU **Tesla T4**, mediante la CLI oficial `google-colab-cli` 0.7.4 (sesión `cafe`, autorizada por el humano con su cuenta). La sesión se cerró al terminar.
- El proceso desatendido `ml/colab_run.py` instaló las dependencias fijadas, comprobó la GPU, descargó los datasets y corrió las fases 1 a 5 comprobando la aceptación de cada una.
- Versiones en Colab (de `history.json`): TensorFlow 2.21.0, Keras 3.15.1, **Python 3.13.15** (en local es 3.12.8).
- La fase 1 se repitió en Colab y su `dataset_stats.json` es **idéntico** al obtenido en local.

### Fase 2 — Entrenamiento

- Hardware: Tesla T4. Tiempo de entrenamiento: 1038.2 s (unos 17 min).
- Se ejecutaron las 15 épocas de la cabeza y las 10 de ajuste fino; `EarlyStopping` no llegó a detener ninguna etapa.
- `class_weight`: minador 2.455, roya 1.004, sana 0.626.
- **Aceptación:** se generan `model.keras`, `labels.txt` y `history.json`; la pérdida de validación baja de 0.671 (época 1) a 0.159 (mínimo, última época de ajuste fino).
- **Curvas:** sin sobreajuste extremo. Al final del ajuste fino la exactitud es 0.910 en entrenamiento y 0.951 en validación (la de entrenamiento se mide con aumento de datos y dropout). La pérdida de validación oscila entre épocas (por ejemplo 0.180 → 0.228 → 0.159) y su mínimo cae en la última época, así que el modelo podría mejorar con más épocas; no se probó.

### Fase 3 — Evaluación y umbral

Sobre test (410 imágenes): exactitud 0.9561, **F1 macro 0.9587**.

| Clase | Precisión | Recall | F1 | Imágenes |
|---|---|---|---|---|
| minador | 0.9649 | 0.9821 | 0.9735 | 56 |
| roya | 0.9286 | 0.9559 | 0.9420 | 136 |
| sana | 0.9718 | 0.9495 | 0.9606 | 218 |

Matriz de confusión (filas = clase real; columnas = predicción minador, roya, sana): `[55, 1, 0]`, `[0, 130, 6]`, `[2, 9, 207]`. Los errores más frecuentes son `sana` predicha como `roya` (9) y `roya` predicha como `sana` (6).

- **Umbral elegido: 0.40**, por la regla del plan (menor umbral con exactitud aceptada ≥ 0.90 en validación).
- **Consecuencia que hay que declarar:** la exactitud en validación sin umbral ya es 0.9513, así que el menor umbral de la lista cumple la meta. Con 0.40 se acepta el 100 % de las imágenes en validación (411 de 411) y en test (410 de 410): **el umbral, tal como lo define el plan, no rechaza nada** en estos datos. La pantalla "No se pudo determinar con seguridad" casi nunca aparecería con hojas parecidas a las del dataset.
- Referencia de la curva en validación: con 0.60 se acepta el 95.86 % con exactitud 0.9619; con 0.80, el 86.37 % con 0.9803; con 0.95, el 64.96 % con 0.9925.
- **Aceptación:** `metrics.json`, `confusion_matrix.png` y `threshold.json` generados. Ninguna clase tiene recall bajo (el menor es 0.9495).

### Fase 4 — Conversión

- `model_fp32.tflite`: 8 901 272 bytes. `model.tflite` (rango dinámico): 2 531 920 bytes, unas 3.5 veces menor.
- **Aceptación:** ambos con entrada `[1,224,224,3] float32` y salida `[1,3] float32` (`model_io.json`, `contract_ok: true`).

### Fase 5 — Paridad y vectores de referencia

- Nivel 1, 100 imágenes de test:
  - Keras vs fp32: 100 % de coincidencia de clase; diferencia máxima de probabilidad 0.000003.
  - Keras vs cuantizado: **98 %** de coincidencia; diferencia máxima de probabilidad **0.143**. Cumple lo esperado (≥ 98 %) justo en el límite: la cuantización cambia la clase en 2 de 100 imágenes.
- Nivel 2: 10 imágenes en `ml/outputs/golden/` (3 minador, 3 roya, 4 sana) con `NN.jpg`, `NN.rgb` (150 528 bytes cada uno) y `golden.json`.
  - El modelo cuantizado acierta la clase real en 9 de 10. La imagen `03` es `roya` y la predice como `sana` (0.744).
- Latencia en la CPU de Colab, solo de referencia: fp32 mediana 13.68 ms (p95 15.79); cuantizado mediana 29.88 ms (p95 34.37). El cuantizado es más lento ahí; en el teléfono puede ser distinto y se mide en la fase 11.
- **Aceptación:** `parity.json` y `golden/` generados. Copiados `model.tflite`, `labels.txt` y `threshold.json` a `android/app/src/main/assets/`, y `golden/` a `android/app/src/androidTest/assets/golden/`.

### Advertencias sobre estas cifras

- Las métricas son sobre imágenes de los mismos datasets. Siguen vigentes las limitaciones de la fase 1 (recortes que pueden venir de fotos de otra partición, varias tomas de una misma hoja en `sana`, fondo blanco en `minador`), que tienden a **inflar** los resultados. La exactitud en campo se mide en la fase 12.
- Para la fase 11: el nivel 2 exige coincidencia de clase en ≥ 9 de 10. Si se compara contra la clase real, Python ya está en 9 de 10 y no queda margen; hay que definir si se compara contra la clase real o contra la que predice TFLite en Python.

### NO EJECUTADO / pendiente

- `ml/colab_entrenamiento.ipynb` sigue **sin probar en el navegador**; la ejecución real fue con `ml/colab_run.py`, que hace los mismos pasos.
- Comparación opcional con EfficientNet-B0 y ResNet50.
- Las imágenes `NN.jpg` y `NN.rgb` de `golden/` no se han subido a git: son imágenes de los datasets y el plan pide a la vez no redistribuir imágenes (fase 0) y copiarlas a `androidTest` (fase 5). Pendiente de decisión del humano.
- Sigue sin confirmar la exclusión de `SANAS_ROCOLE_*`; si se cambia, hay que repetir las fases 1 a 5.

## Fase 6 — Proyecto Android: base (2026-10-10)

**Estado: CERRADA.** Criterio de aceptación cumplido: `./gradlew assembleDebug` compila y la app abre sin fallar.

### Qué se hizo

- Proyecto Compose en `android/`: paquete `co.edu.unipamplona.cafedetector`, `minSdk 26`, un módulo `app`, `gradle/libs.versions.toml`, wrapper de Gradle 9.8.1.
- Dependencias del plan (CameraX, LiteRT, lifecycle-viewmodel-compose, navigation-compose, kotlinx-serialization) con versiones verificadas en su fuente.
- `noCompress += "tflite"`; manifiesto con permiso `CAMERA` y cámara no obligatoria; sin `INTERNET`.
- `MainActivity` mínima que muestra el título y el aviso de herramienta de apoyo, ambos desde `strings.xml`.

### Qué se comprobó

- `./gradlew assembleDebug`: compila. APK de depuración: 38 455 400 bytes.
- Emulador `Medium_Phone_API_37.0` (Android 17, API 37, x86_64): la app se instala, abre en 1423 ms, el proceso sigue vivo y no hay ningún `FATAL EXCEPTION` en logcat. Captura revisada: se ven el título y el aviso.
- `aapt2 dump permissions`: **no hay `INTERNET`**.
- `model.tflite` va sin comprimir dentro del APK (2 531 920 bytes almacenados).

### Hallazgo que hay que revisar en la fase 10

LiteRT 2.3.0 arrastra dependencias (`play:asset-delivery`, `work-runtime`, `media3-common`) que añaden al manifiesto permisos que la app no pidió: `ACCESS_NETWORK_STATE`, `WAKE_LOCK`, `RECEIVE_BOOT_COMPLETED`, `FOREGROUND_SERVICE` y `FOREGROUND_SERVICE_DATA_SYNC`. Ninguno es `INTERNET`, así que la regla del plan se cumple, pero no encajan con una app sin conexión y contribuyen al tamaño del APK. Opciones para la fase 10: quitarlos del manifiesto o cambiar a la librería clásica `org.tensorflow:tensorflow-lite`, que el plan también permite.

### NO EJECUTADO / pendiente

- `conditions.json` todavía no está en `assets/` (es la fase 7 y necesita el texto del informe).
- Prueba en teléfono físico (fase 12).

## Fase 7 — Contenido informativo (2026-10-10)

**Estado: CERRADA.** Criterio de aceptación cumplido: cada línea de `labels.txt` tiene entrada en `conditions.json` (prueba unitaria en verde).

### Qué se hizo

- `android/app/src/main/assets/conditions.json` con una ficha por clase. Fuente: el informe aportado por el humano (`docs/Protocolo de entrega del Documento final de Proyecto_cursos 2026_2 (1).docx`).
  - `sintomas` de minador y roya: texto de las secciones 1.2.1.2 y 1.2.2.1 (sin el prefijo "Descripción:").
  - `condiciones` de minador y roya: las frases sobre condiciones favorables de las secciones 1.1.1.2 y 1.1.2.1.
  - `sana`: el texto que da el propio plan.
- `data/ConditionsRepository.kt`, que lo carga con `kotlinx.serialization`.
- Prueba unitaria `ConditionsTest` (`labels.txt` ↔ `conditions.json`).

### Qué se comprobó

- `./gradlew testDebugUnitTest assembleDebug`: compila y la prueba pasa (1 prueba, 0 fallos).
- No se incluyó ninguna recomendación de manejo.

### Fidelidad al informe

Los textos son copia literal, con dos retoques de puntuación en la ficha del minador: se quitó un espacio doble y se añadió el punto que faltaba entre "los niveles de la plaga" y "Si la temperatura". **No se corrigió la redacción.** La frase de la roya conserva su forma original ("la humedad relativamente superior al 70%", "condiciones que prolonga la permanencia de la humedad y favorecer el desarrollo"), que tiene errores de concordancia; conviene corregirla primero en el informe y luego aquí.

### NO EJECUTADO / pendiente

- No se observó la prueba en rojo antes de implementarla: el archivo y la prueba se escribieron a la vez.
- `conditions.json` todavía no se muestra en pantalla (fase 9).

## Fase 8 — Clasificador (2026-10-10)

**Estado: NO CERRADA.** Su criterio es "pruebas de la fase 11 en verde" y una prueba instrumentada falla (paridad nivel 1). Se necesita una decisión del humano.

### Qué se hizo

- `ml/ClassifierLogic.kt`: `Prediction`, `ClassificationResult`, selección del top-3, regla de umbral y lectura de `threshold.json`, sin dependencias de Android para poder probarlo en la JVM.
- `ml/CoffeeLeafClassifier.kt`: según el plan (una instancia, llamadas sincronizadas, `classify(bitmap)` y `classifyRgbBytes`). Carga el modelo con `assets.openFd` + `FileChannel.map` y falla con un mensaje claro si el número de salidas no coincide con `labels.txt`. La app no normaliza la imagen.
- `ml/ImageUtils.kt`: decodificación con muestreo previo, rotación EXIF, rotación de fotos de CameraX y conversión a `ARGB_8888`.
- Pruebas unitarias (`ClassifierLogicTest`) e instrumentadas (`CoffeeLeafClassifierTest`).

### Qué se comprobó

- **Unitarias: 8 de 8 en verde** (top-3, umbral, `threshold.json`, `labels.txt` ↔ `conditions.json`, muestreo).
- **Instrumentadas en el emulador** (`sdk_gphone64_x86_64`, Android 17, x86_64): 3 de 4 en verde.
  - `labels.size` = nº de salidas del modelo: pasa.
  - **Nivel 2, flujo completo con los `.jpg`: 10 de 10 clases coinciden** (se exige ≥ 9). Se compara contra la clase que predice TFLite en Python, porque es una prueba de paridad.
  - Latencia en el emulador (4 hilos, 5 de calentamiento + 50 medidas): mediana 14.0 ms, p95 16 ms. Es un emulador en un PC, no un teléfono.
  - **Nivel 1, modelo aislado con los `.rgb`: FALLA.** La clase coincide en las 10 imágenes, pero la diferencia máxima de probabilidad supera 0.01 en 2 de ellas: `03` (0.0138) y `07` (0.0152). En las otras 8 es ≤ 0.0017.
- Un error propio corregido por el camino: `ImageUtils.decodeUpright` devolvía siempre `null` (trataba como fallo el `null` que el decodificador devuelve a propósito al leer solo las dimensiones).

### Diagnóstico del fallo de nivel 1

Se hizo una prueba de diagnóstico temporal (ya borrada) en el emulador y en Python local:

- Con el modelo **fp32**, Android y Python coinciden con diferencia < 0.0001 en las 10 imágenes. El preprocesado, el contrato de la sección 4 y la ruta de inferencia de la app están bien.
- Con el modelo **cuantizado**, el resultado depende de qué implementación de los núcleos ejecuta la CPU:
  - Python en Colab, Python local con TensorFlow 2.21.0 y Python local con LiteRT 2.3.0 dan exactamente lo mismo (diferencia 0.0000).
  - Python local **sin** XNNPack difiere hasta 0.0344, y Android sin XNNPack da esas mismas diferencias (0.0344 y 0.0240).
  - Android con XNNPack difiere 0.0138 y 0.0152. La CPU del emulador expone AVX pero no AVX2, así que usa otros núcleos que el PC.
- Conclusión: la cuantización de rango dinámico no es numéricamente idéntica entre CPUs. Las dos imágenes afectadas son las de menor confianza (0.744 y 0.761), donde un cambio pequeño en los valores internos mueve más la probabilidad. En un teléfono ARM cabe esperar otra diferencia distinta.

### Pendiente de decisión del humano

El plan pide a la vez modelo cuantizado de rango dinámico (fase 4) y diferencia < 0.01 en el nivel 1 (fase 11); con este modelo y este emulador no se cumplen las dos cosas. No se ha relajado la tolerancia ni cambiado el modelo.

### NO EJECUTADO

- Pruebas en dispositivo físico ARM.

## Fase 8 — Cierre (2026-10-10)

**Estado: CERRADA.** Criterio cumplido: las pruebas de la fase 11 que corresponden al clasificador están en verde.

### Qué cambió

- Por decisión del humano, la app lleva el modelo sin cuantizar (ver `docs/decisiones.md`).
- `ml/05_paridad_tflite.py` calcula ahora `probs_tflite` con el modelo que se entrega. Se volvió a ejecutar **en el PC local** (el plan sitúa la paridad Keras vs TFLite en el PC); no hubo entrenamiento ni evaluación nuevos.
- Los `.rgb` regenerados son idénticos byte a byte a los de Colab y las 10 imágenes son las mismas.

### Qué se comprobó

- Unitarias: 8 de 8 en verde.
- Instrumentadas en el emulador (`sdk_gphone64_x86_64`, Android 17, x86_64): **4 de 4 en verde**.
  - Nivel 1: diferencia máxima de probabilidad 0.0000017 (límite 0.01).
  - Nivel 2: 10 de 10 clases coinciden (se exige ≥ 9).
  - Latencia con 4 hilos: mediana 9.0 ms, p95 12 ms. Es un emulador en un PC, no un teléfono.
- APK de depuración: 47 379 018 bytes.

### `parity.json` actualizado (ejecución local)

- Keras vs fp32: 100 % de coincidencia de clase; diferencia máxima 0.0022 (en Colab fue 0.000003; aquí Keras corre en la GPU local).
- Keras vs cuantizado: 98 % de coincidencia; diferencia máxima 0.145.
- Latencia en el PC local, solo de referencia: fp32 mediana 6.46 ms; cuantizado 9.03 ms.

### Lo que el modelo fp32 no arregla

"Más exacto" significa aquí que la app da las mismas probabilidades que el modelo evaluado en la fase 3. No significa que acierte más: la imagen de referencia `03` es `roya` y el modelo fp32 también la predice como `sana` (0.578). Las métricas de la fase 3 no cambian.

### NO EJECUTADO

- Pruebas en dispositivo físico ARM (fase 12).

## Fase 9 — Interfaz (2026-10-10)

**Estado: CERRADA.** Criterio cumplido en el emulador: flujo foto → resultado completo y la rotación no pierde el estado.

### Qué se hizo

- `ui/ClassifierViewModel.kt` (`UiState` como `StateFlow`, clasificador creado una vez en hilo de fondo y cerrado en `onCleared()`, clasificación en `Dispatchers.Default`, errores como recursos de texto, miniatura de ~512 px).
- `ui/HomeScreen.kt`, `ui/CameraScreen.kt`, `ui/ResultScreen.kt`, `ui/Theme.kt`, `ui/Components.kt`, `ui/Formatting.kt` y `MainActivity.kt` con `NavHost` (rutas `home`, `camera`, `result`).
- Todos los textos en `strings.xml`, en español; `contentDescription` en imágenes y botón de captura.
- La escritura se delegó a un agente; la maqueta de v0 (`docs/maqueta-v0/`, React con estilo iOS) se usó solo como referencia de colores, distribución y textos. Las pantallas son Material 3, como pide el plan.

### Qué se comprobó en el emulador (Android 17, x86_64)

- `./gradlew testDebugUnitTest assembleDebug`: compila; 11 pruebas unitarias en verde (3 nuevas de formato del porcentaje).
- **Cámara → resultado:** inicio → "Tomar foto" → vista previa con marco guía → captura → pantalla de resultado con miniatura, clase, barra de confianza, top-3 y ficha.
- **Galería → resultado:** una hoja con roya del dataset elegida con el selector de fotos se clasifica como "Roya del café" y muestra su ficha con "Síntomas" y "Condiciones favorables".
- **Rotación:** al girar la pantalla en el resultado, el resultado sigue ahí.
- **Permiso denegado:** aparece la pantalla explicativa; "Abrir ajustes" abre los ajustes de la app y "Volver al inicio" regresa.
- Sin cierres inesperados en logcat durante todo el recorrido. El APK sigue sin `INTERNET`.

### Hallazgo importante para el informe

La cámara del emulador muestra una sala virtual (un mueble y un televisor), no una hoja. La app la clasificó como **"Hoja sana" con 100 % de confianza**. Confirma el aviso de la fase 3: el modelo nunca vio "otras cosas" y el umbral de 0.40 no rechaza nada. La clase opcional `no_hoja` (v1.1 del plan) es la mitigación prevista.

### Diferencias respecto a la maqueta y al encargo

- El verde principal es más oscuro que el de la maqueta, para tener contraste suficiente.
- No hay iconos: "Atrás" y "Cancelar" son botones de texto, porque no se añadió la dependencia de iconos.
- La captura se pide a unos 1280×960 para no gastar memoria en una entrada de 224 px.
- Con confianza baja no se muestra el top-3 (el plan pide mensaje y consejos, sin ficha).

### NO EJECUTADO

- La pantalla "No se pudo determinar con seguridad": no se pudo provocar, porque con el umbral 0.40 ninguna imagen probada queda por debajo.
- Los estados de error (archivo corrupto, modelo que no carga, poca memoria) y el diálogo "Acerca de" no se recorrieron en el emulador.
- Recuperación tras muerte del proceso: el resultado no se restaura (vuelve al inicio).
- Prueba en teléfono físico y con hojas reales (fase 12).

## Fase 10 — Rendimiento y robustez (2026-10-10)

**Estado: CERRADA** en lo que puede comprobarse en el emulador. El plan no define un criterio de aceptación para esta fase.

### Qué se hizo

- Pruebas instrumentadas nuevas (`RobustnessTest`): archivo corrupto, JPEG truncado, imagen de 12 MP, rotación EXIF y comparación de hilos.
- Se quitaron del manifiesto cinco permisos que añadían las dependencias de LiteRT (ver `docs/decisiones.md`).

### Qué se comprobó

- El modelo se carga al crear el ViewModel, en un hilo de fondo (`Dispatchers.Default`).
- **Archivo corrupto, vacío o ilegible:** `decodeUpright` devuelve `null` y no lanza excepción; el ViewModel lo muestra como error.
- **JPEG truncado:** no provoca fallo.
- **Imagen enorme (4000×3000, 12 MP):** se decodifica submuestreada a 1000×750 en `ARGB_8888` y se clasifica.
- **Rotación EXIF:** una imagen 600×480 marcada como rotada 90° sale 480×600.
- **Permiso denegado:** comprobado en la fase 9.
- **Permisos del APK** (`aapt2 dump permissions`): solo `CAMERA` y un permiso interno de AndroidX. **Sin `INTERNET`** y sin los cinco que añadía LiteRT. Con ellos quitados, la app abre, muestra "Acerca de" (versión `v1-2026-10` y créditos) y completa cámara → resultado sin fallos.
- **Hilos (2 vs 4)**, emulador, 5 de calentamiento + 50 medidas por configuración:
  - 2 hilos: mediana 9.0 ms, p95 11 ms.
  - 4 hilos: mediana 12.0 ms, p95 15 ms.
  - Las 10 predicciones de referencia son idénticas con 2 y con 4 hilos.
  - **No es concluyente:** en la misma ejecución, otra prueba con 4 hilos midió mediana 9.0 ms. Las diferencias están dentro del ruido del emulador.
- APK de depuración: 45 702 962 bytes.

### NO EJECUTADO

- Delegado GPU (opcional en el plan).
- **Poca memoria** y **cámara no disponible:** el código los maneja (captura de `OutOfMemoryError`, pantalla "Cámara no disponible"), pero no se provocaron en el emulador.
- Medición de hilos en un teléfono real.

## Fase 11 — Pruebas (2026-10-10)

**Estado: CERRADA.** Criterio cumplido: todas pasan en un emulador x86_64 (`sdk_gphone64_x86_64`, Android 17).

| Conjunto | Pruebas | Resultado |
|---|---|---|
| Unitarias (`src/test`) | 11 | 11 en verde |
| Instrumentadas (`src/androidTest`) | 9 | 9 en verde |

- Unitarias: top-3 y regla de umbral con probabilidades simuladas, `labels.txt` ↔ `conditions.json`, lectura de `threshold.json`, muestreo y formato del porcentaje.
- Instrumentadas:
  - Nivel 1 (modelo aislado, `.rgb`): misma clase en las 10; diferencia máxima de probabilidad 0.0000017 (límite 0.01).
  - Nivel 2 (flujo completo, `.jpg`): 10 de 10 clases coinciden (se exige ≥ 9).
  - Latencia: mediana 9.0 ms, p95 11 ms, 4 hilos, guardada en `latency.json` junto con el modelo del dispositivo.
  - `labels.size` = nº de salidas del modelo.
  - Las cinco de robustez de la fase 10.
- Los archivos de resultados del emulador se copiaron a `ml/outputs/android_emulator/`.

### NO EJECUTADO

- Las mismas pruebas en un dispositivo físico (fase 12). Las latencias del emulador no representan un teléfono.

## Fase 12 — Evaluación en campo y documentación (2026-10-10)

**Estado: NO CERRADA.** Falta todo lo que requiere un teléfono y fotos reales del humano.

### Qué se hizo

- `ml/generar_resultados.py` y `make results`: generan `docs/resultados.md` a partir de `ml/outputs/`, sin cifras escritas a mano. Incluye métricas por clase, matriz de confusión, cobertura frente a exactitud del umbral, tamaños, paridad, latencia del emulador y limitaciones.
- `README.md` con los pasos para reproducir.
- La sección de resultados en campo se rellena sola cuando exista `docs/campo.csv` (columnas `foto,clase_real,prediccion,confianza`) y siempre indica que n es pequeño.

### Qué se comprobó

- `make results` se ejecuta y el archivo generado coincide con los JSON de origen.

### NO EJECUTADO

- **Paso 1:** instalar el APK en un teléfono de gama media y anotar modelo y versión de Android.
- **Paso 2:** probar con fotos reales tomadas por el humano (sol directo, sombra, fondo complicado, hoja con y sin enfermedad) y calcular la exactitud en campo.
- **Paso 3:** latencia en teléfono. El tamaño sí está medido: APK de depuración 45 702 962 bytes; modelo entregado 8 901 272 bytes.
- El comando `./gradlew connectedDebugAndroidTest` que cita el README no se ejecutó tal cual: las pruebas instrumentadas se lanzaron con `adb shell am instrument`, para poder leer los archivos de resultados antes de desinstalar.
- Comparación opcional de modelos (EfficientNet-B0, ResNet50).

## Fase 12 — Pasos 1 y 3: teléfono físico (2026-10-10)

**Estado: la fase sigue SIN CERRAR.** Falta el paso 2 (fotos reales del humano).

### Qué se hizo

- Se instaló el APK de depuración en el teléfono del humano por USB y se ejecutaron en él las pruebas instrumentadas.
- Los archivos de resultados se guardaron en `ml/outputs/android_phone/` y `docs/resultados.md` incluye ahora una sección del teléfono.

### Qué se comprobó

- Dispositivo: **Motorola Edge 30**, Android 14 (API 34), arm64-v8a, SoC SM7325, unos 7.2 GB de RAM.
- La app se instala, abre en 1668 ms y no registra cierres inesperados.
- **Pruebas instrumentadas: 9 de 9 en verde en el teléfono.**
  - Nivel 1: diferencia máxima de probabilidad 0.0000001 (límite 0.01).
  - Nivel 2: 10 de 10 clases coinciden.
- **Latencia:** mediana 21.0 ms, p95 22 ms con 4 hilos (5 de calentamiento + 50 medidas).
- **Hilos:** 2 hilos, mediana 21.0 ms y p95 23 ms; 4 hilos, mediana 21.0 ms y p95 22 ms. No hay diferencia apreciable; se mantiene 4, y las predicciones son idénticas.
- Tamaño: APK de depuración 45 702 962 bytes; modelo 8 901 272 bytes.

### NO EJECUTADO

- Paso 2: fotos reales tomadas por el humano y exactitud en campo.
- Recorrido manual de la interfaz en el teléfono por parte del agente (solo se comprobó que abre).
