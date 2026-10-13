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

## Fase 12 — Validación externa con BRACOL (2026-10-10)

**Estado: la fase sigue SIN CERRAR.** El paso 2 del plan (fotos reales tomadas por el humano) no se ha hecho; esto es una prueba adicional pedida por el humano.

### Qué se hizo

- Descarga de BRACOL (café arábica, Brasil, CC BY 4.0) a `ml/data/external/` (fuera de git).
- `BatchClassificationTest`: prueba instrumentada que pasa todas las fotos de una carpeta por el mismo camino de la app (`decodeUpright` + `classify`) y escribe un CSV. Sirve también para las fotos del humano.
- Las 860 imágenes se clasificaron **en el teléfono** (Motorola Edge 30) en 31 s. Predicciones en `ml/outputs/external_bracol/predicciones_telefono.csv`; métricas en `metrics.json` de la misma carpeta. Las imágenes se borraron del teléfono al terminar.

### Resultado

| | Test interno (fase 3) | BRACOL externo |
|---|---|---|
| Imágenes | 410 | 860 |
| Exactitud | 0.9561 | **0.6872** |
| F1 macro | 0.9587 | **0.6260** |

| Clase | Precisión | Recall | F1 | Imágenes |
|---|---|---|---|---|
| minador | 0.6807 | 0.4466 | 0.5394 | 253 |
| roya | 0.6748 | 0.8925 | 0.7685 | 465 |
| sana | 0.7975 | 0.4437 | 0.5701 | 142 |

Matriz de confusión (filas = clase real; columnas = minador, roya, sana): `[113, 132, 8]`, `[42, 415, 8]`, `[11, 68, 63]`.

### Lectura

- **El modelo no generaliza a este dataset.** Fuera de los datos de entrenamiento la exactitud cae 27 puntos.
- **Sesgo hacia `roya`:** más de la mitad de las hojas con minador (132 de 253) y casi la mitad de las sanas (68 de 142) salen como roya.
- **Confianza mal calibrada:** 49 errores tienen confianza ≥ 0.9, y solo 1 imagen de 860 queda por debajo del umbral 0.40. El umbral no protege.
- Es coherente con las advertencias de las fases 1 y 3 (fugas que inflan el test, sesgo de fondo, softmax sobreconfiado).

### Cautelas sobre esta prueba

- BRACOL son hojas sobre fondo blanco, no fotos de campo, y la etiqueta es el estrés **predominante**: una hoja puede tener además otros daños.
- En el entrenamiento, las hojas sobre fondo blanco eran sobre todo de minador y de roya, y casi ninguna sana. No se ha comprobado cuánto del error se debe al fondo.
- No se investigaron las causas ni se reentrenó.

### NO EJECUTADO

- Paso 2 de la fase 12: fotos reales tomadas por el humano (sol, sombra, fondo complicado) y exactitud en campo.

## Reentrenamiento v2 — R0: diagnóstico (2026-10-10)

El humano decidió reentrenar tras la validación externa, manteniendo las tres clases. Plan en `docs/PLAN_reentrenamiento_v2.md`. Este paso es solo diagnóstico, con el modelo v1 y en el PC local.

### Hallazgo 1: la partición de la fase 1 quedó sesgada por origen (error propio)

| Partición | Imágenes | De RoCoLe |
|---|---|---|
| train | 1915 | 67.2 % |
| val | 411 | 3.6 % |
| test | 410 | 2.7 % |

- El test interno tiene solo 11 imágenes de RoCoLe (todas de roya, ninguna sana), aunque RoCoLe aporta 1313 imágenes al conjunto. También la roya de DECAFIA quedó descompensada: 89 en train, 126 en val y 125 en test.
- **Causa:** el algoritmo de reparto que escribí en `01_preparar_datos.py` asigna primero los grupos grandes y los manda a train hasta llenar su cuota; las plantas de RoCoLe (varias fotos cada una) son los grupos grandes. El reparto se estratificó por clase, no por origen, y las comprobaciones de aceptación (fugas, mínimo por clase, desbalance) no lo detectan.
- **Consecuencia:** las métricas de la fase 3 (exactitud 0.9561, F1 macro 0.9587) miden casi solo imágenes de DECAFIA. **No dicen cómo rinde el modelo en RoCoLe**, y validación y test no representan lo que se entrenó. El umbral también se eligió con esa validación sesgada.

### Hallazgo 2: el fallo en BRACOL no se explica solo por el fondo blanco

Mismo modelo, mismas 860 imágenes, tres variantes (clasificación en Python con el modelo fp32):

| Variante | Exactitud | Recall minador | Recall roya | Recall sana |
|---|---|---|---|---|
| Imagen original | 0.6860 | 0.474 | 0.890 | 0.394 |
| Recortada a la hoja | 0.5093 | 0.822 | 0.329 | 0.542 |
| Fondo blanco sustituido por un tono oscuro | 0.6651 | 0.340 | 0.927 | 0.387 |

- Cambiar el color del fondo casi no mueve el resultado, así que "fondo blanco = cierta clase" no es la explicación principal.
- Recortar a la hoja lo empeora y vuelca las predicciones hacia `minador` (545 de 860). El modelo es sensible al encuadre y a la escala: en el entrenamiento, los acercamientos eran en buena parte recortes de minador.
- Conclusión: no hay un único atajo que corregir; el modelo generaliza mal por falta de variedad en los datos. La exactitud original en Python (0.6860) y en el teléfono (0.6872) difieren en una imagen, lo esperable por la decodificación.

### NO EJECUTADO

- No se midió el rendimiento del modelo v1 sobre RoCoLe con una partición correcta.

## Reentrenamiento v2 — R1 a R3: datos, reparto y tubería de entrenamiento (2026-10-10)

**Estado: R1, R2 y R3 hechos en local. R4 (entrenamiento en Colab) pendiente.** La escritura se delegó a un agente; lo que sigue se volvió a comprobar después.

### Qué se hizo

- `ml/01_preparar_datos.py`: fuente BRACOL, reparto estratificado por origen y clase, imágenes procesadas a 512 px de lado mayor, comprobación de equilibrio por origen.
- `ml/02_entrenar.py`: argumentos `--arch`, `--run` y `--holdout-source`; aumento de datos más fuerte (rotación, acercamiento y alejamiento, traslación, brillo, contraste, tono y saturación); pesos por estrato; ajuste fino de toda la red con las `BatchNormalization` congeladas; suavizado de etiquetas.
- `ml/03_evaluar.py`: métricas del test interno, por origen y de la fuente apartada; error de calibración; umbral elegido con la fuente apartada.
- `ml/colab_run_v2.py` y `make colab-data` (genera `cafe_data_v2.zip`, fuera de git).
- `ml/tests/test_split.py`: prueba del reparto con datos sintéticos.

### Qué se comprobó

- **Prueba del reparto:** falla con el algoritmo antiguo (reproduce el sesgo: un estrato con 95.7 % en entrenamiento) y pasa con el nuevo (4 de 4).
- **`make data`:** 3596 imágenes (RoCoLe 1313, DECAFIA 1423, BRACOL 860). Fugas: 0 por MD5, 0 por hash perceptual, 0 grupos repartidos. Equilibrio por origen: 8 estratos comprobados, desviación máxima 0.0042 respecto a 70/15/15.

| Partición | BRACOL (minador / roya / sana) | DECAFIA (minador / roya / sana) | RoCoLe (roya / sana) |
|---|---|---|---|
| train | 177 / 326 / 100 | 261 / 238 / 499 | 398 / 522 |
| val | 38 / 70 / 21 | 56 / 51 / 106 | 85 / 112 |
| test | 38 / 69 / 21 | 55 / 51 / 106 | 85 / 111 |

- BRACOL descartado: 329 filas sin imagen (archivo truncado), 1 ilegible, y 557 de clases que no son de la v1.
- **Prueba de humo** de entrenamiento y evaluación con una época por etapa, para las dos arquitecturas: corre y produce todos los archivos; ambos modelos guardados aceptan `float32 [1,224,224,3]` en 0–255 y devuelven `[1,3]`. Los archivos se borraron; ninguna cifra suya se usa.

### NO EJECUTADO

- `ml/colab_run_v2.py` no se ha ejecutado nunca.
- Entrenamiento real (R4).
- La descarga del conjunto final (JMuBEN) sigue en curso; no se ha abierto.
- `04_convertir_tflite.py`, `05_paridad_tflite.py` y `generar_resultados.py` aún no están adaptados a la nueva estructura de carpetas (R5).

## Reentrenamiento v2 — R4, etapa 1: selección de arquitectura (2026-10-11)

**Estado: etapa 1 hecha. Etapa 2 (modelo final) lanzada en Colab.**

### Cómo se ejecutó

- Google Colab, Tesla T4, con `ml/colab_run_v2.py`. Datos subidos ya preparados (`cafe_data_v2.zip`, en 10 partes de 16 MB porque la subida en una sola petición fallaba; SHA-256 comprobado al unirlas).
- Las dos arquitecturas se entrenaron con RoCoLe y DECAFIA únicamente. BRACOL (860 imágenes) quedó fuera del entrenamiento y de la validación y se usó solo para medir.
- Resultados en `ml/outputs/stage1_mobilenetv2/` y `ml/outputs/stage1_efficientnetb0/`.

### Resultado

| | v1 (MobileNetV2) | v2 MobileNetV2 | v2 EfficientNet-B0 |
|---|---|---|---|
| BRACOL, exactitud | 0.6872 | 0.7767 | **0.8581** |
| BRACOL, F1 macro | 0.6260 | 0.7313 | **0.8494** |
| BRACOL, recall minador | 0.4466 | 0.3676 | 0.6087 |
| BRACOL, recall roya | 0.8925 | 0.9419 | 0.9613 |
| BRACOL, recall sana | 0.4437 | 0.9648 | 0.9648 |
| Test interno, F1 macro | 0.9587 (test sesgado) | 0.9819 | 0.9900 |
| Tiempo de entrenamiento | 1038 s | 1206 s | 1337 s |
| Épocas (cabeza + ajuste fino) | 15 + 10 | 10 + 24 | 10 + 26 |

- **Arquitectura elegida: EfficientNet-B0**, por la regla del plan (mayor F1 macro en la fuente no vista).
- Por origen, en el test interno (EfficientNet-B0): DECAFIA 212 de 212; RoCoLe exactitud 0.9745 (roya recall 0.9529, sana 0.9910). Es la primera vez que hay una cifra fiable para RoCoLe.
- Matriz de confusión de EfficientNet-B0 en BRACOL (filas = clase real; columnas = minador, roya, sana): `[154, 84, 15]`, `[17, 447, 1]`, `[0, 5, 137]`.

### Lectura

- La mejora en BRACOL es real y no se debe a haberlo visto: ningún modelo de esta etapa se entrenó con BRACOL.
- **Punto débil que persiste:** el minador. Con EfficientNet-B0, 84 de 253 hojas con minador se confunden con roya (recall 0.61).
- Las hojas sanas pasan de 0.44 a 0.96 de recall.
- Calibración (error esperado, 15 intervalos): EfficientNet-B0 0.083 en el test interno y 0.109 en BRACOL; MobileNetV2 0.081 y 0.039.
- Umbral elegido con BRACOL: 0.55 para EfficientNet-B0 (acepta el 99.3 % del test interno, con exactitud 0.9926) y 0.85 para MobileNetV2.

### Cautelas

- BRACOL sirvió para **elegir** la arquitectura y el umbral, así que sus cifras ya no son una estimación limpia. La estimación limpia es el conjunto final (JMuBEN), que sigue sin abrirse.
- El test interno de la v1 y el de la v2 no son comparables: tienen distinto reparto y la v1 no incluía casi nada de RoCoLe.
- Un solo entrenamiento por arquitectura, con una sola semilla: no se midió la variabilidad entre ejecuciones.
- Cambia el modelo base respecto al plan original, que fijaba MobileNetV2 y dejaba EfficientNet-B0 como comparación opcional.

## Reentrenamiento v2 — R4 etapa 2 y R5: modelo final y cierre (2026-10-11)

**Estado: R4 y R5 CERRADOS.** Sigue sin ejecutarse la prueba de campo con fotos del humano (fase 12, paso 2).

### Modelo final (etapa 2)

- EfficientNet-B0 entrenado en Colab (Tesla T4) con las tres fuentes: 1483.8 s, 10 épocas de cabeza y 23 de ajuste fino (la parada temprana cortó antes de las 40). Pérdida de validación: 0.6837 en la época 1, mínimo 0.3447.
- Test interno, equilibrado por origen (536 imágenes): exactitud 0.9907, F1 macro 0.9902. Por origen: DECAFIA 1.0000 (212), RoCoLe 0.9847 (196), BRACOL 0.9844 (128).
- La sesión de Colab se cerró al descargar los resultados.

### Conversión y paridad (PC local)

- `model_fp32.tflite`: 16 072 468 bytes. `model.tflite` (rango dinámico): 4 572 672 bytes. Ambos cumplen el contrato de la sección 4.
- Keras vs fp32: 100 % de coincidencia de clase, diferencia máxima 0.00097. Keras vs cuantizado: 100 %, diferencia máxima 0.136.
- La app lleva el fp32. Vectores de referencia regenerados (10 imágenes; el modelo acierta la clase real en las 10).

### Umbral

0.55, tomado de la etapa 1 (ver `docs/decisiones.md`). `ml/outputs/final/threshold.json` se escribió a mano con ese valor; `threshold_source.json` documenta su origen. `metrics.json` conserva el 0.40 que da la regla sobre la validación interna.

### Pruebas con el modelo v2

- Unitarias: 11 de 11.
- Instrumentadas en el teléfono (Motorola Edge 30, Android 14): todas en verde (la de lote se omite porque no había fotos cargadas).
  - Nivel 1: diferencia máxima 0.0000004. Nivel 2: 10 de 10.
  - Latencia: mediana 48.0 ms, p95 48 ms con 4 hilos; igual con 2 hilos (el modelo v1 medía 21 ms).
- La app abre en el teléfono sin cierres inesperados. APK de depuración: 61 775 482 bytes.

### Conjunto final (JMuBEN), abierto una sola vez

Modelo, umbral y código se confirmaron en git (commit `6297064`) antes de abrirlo. 44 298 archivos; 1 ilegible; 44 297 evaluados con el modelo fp32 que lleva la app.

| | v1 | v2 (final) |
|---|---|---|
| Exactitud | 0.6137 | **0.8003** |
| F1 macro | 0.5895 | **0.7658** |
| Recall minador | 0.3374 | 0.5458 |
| Recall roya | 0.8388 | 0.8637 |
| Recall sana | 0.7619 | 1.0000 |
| Precisión roya | 0.3486 | 0.5011 |

Matriz de confusión del v2 (filas = clase real; columnas = minador, roya, sana): `[9266, 7168, 544]`, `[224, 7200, 912]`, `[0, 0, 18983]`.

- Con el umbral 0.55 se acepta el 93.6 % de las imágenes, con exactitud 0.8196 sobre las aceptadas.
- Error de calibración esperado: 0.1198 (confianza media 0.766, exactitud 0.800).
- El v1 se midió después sobre el mismo conjunto solo como referencia; no se usó para decidir nada.

### Lectura

- **El reentrenamiento mejoró de verdad:** en datos nunca usados, la exactitud sube de 0.61 a 0.80 y el F1 macro de 0.59 a 0.77.
- **No está resuelto:** el modelo sigue confundiendo minador con roya. Reconoce el 55 % de las hojas con minador (7168 de 16 978 las da como roya) y solo la mitad de lo que llama roya lo es.
- La brecha entre el test interno (0.99) y el conjunto final (0.80) confirma que el test interno no mide generalización.

### Cautelas

- JMuBEN son recortes de hoja ampliados con aumento de datos por sus autores: muchas imágenes derivan de una misma foto, así que 44 297 no son 44 297 hojas independientes.
- No son fotos de campo de hojas completas ni de Colombia.
- Un solo entrenamiento, una sola semilla.

### Otros cambios

- `docs/resultados.md` regenerado con la estructura nueva; `README.md`, `docs/MANUAL_WINDOWS.md` y el `Makefile` actualizados al modelo v2 (`RUN ?= final`).

### NO EJECUTADO

- Fotos reales del humano en campo (fase 12, paso 2).
- Pruebas instrumentadas del modelo v2 en el emulador (se hicieron en el teléfono).
- `ml/colab_entrenamiento.ipynb` quedó desactualizado: corresponde a la v1.
- El camino de Colab desde el navegador descrito en el manual de Windows.

## Versión instalable (2026-10-11)

### Qué se hizo

- Ícono adaptativo de la app (`res/drawable/ic_launcher_*.xml`, `res/mipmap-anydpi-v26/`).
- Firma de la compilación `release` leída de `android/keystore.properties` (fuera de git); sin ese archivo, la compilación queda sin firmar.
- APK firmado en `dist/DetectorHojasCafe-v2.0.apk`.

### Qué se comprobó

- `./gradlew testDebugUnitTest assembleRelease`: compila; pruebas unitarias en verde.
- `apksigner verify`: firma válida, certificado `CN=Detector de hojas de cafe, O=Universidad de Pamplona`.
- APK: 47 442 771 bytes, versión 2.0, permisos `CAMERA` y uno interno de AndroidX, sin `INTERNET`. SHA-256 `c9f0154b10c8256f38b027b2aef5506020103e7d68d143b1a0ac55093d73550b`.
- Instalado en el teléfono (Motorola Edge 30) tras desinstalar la versión de depuración: abre sin cierres inesperados.
- Instalado en el emulador: abre, y el ícono se ve correcto en la pantalla de información de la app.

### NO EJECUTADO

- No se vio el ícono en el teléfono: tenía la pantalla apagada al capturar.
- No se recorrió el flujo foto → resultado con la compilación `release` (solo se comprobó que abre). Las pruebas instrumentadas se hicieron sobre la compilación de depuración del mismo código y modelo.
- El código no está ofuscado ni reducido (`isMinifyEnabled = false`).

## Página de descarga (2026-10-11)

### Qué se hizo

- El humano generó la plantilla con v0 (`docs/landing-detector-hojas-cafe`, Next.js). Se refinó con las skills `impeccable` y `design-taste-frontend` hacia el estilo de listas agrupadas tipo iOS que ya tienen las pantallas de la app. La escritura se delegó a un agente.
- Se añadieron a `public/` el APK firmado, el ícono real y dos capturas reales de la app tomadas en el emulador con el modelo v2 (inicio y un resultado de roya al 93 %).
- Se quitó la dependencia de analítica de la plantilla y los recursos de relleno de v0; el título, la descripción y el idioma de la página se corrigieron.
- Paquete para publicar: `dist/landing-detector-hojas-cafe.zip` (sin `node_modules` ni `.next`).

### Qué se comprobó

- `pnpm build` compila con comprobación de tipos (la plantilla de v0 la tenía desactivada).
- Capturas en móvil (390×844) y escritorio (1440×900), revisadas: el aviso de prototipo, el botón de descarga y la línea de versión quedan visibles sin desplazarse.
- El enlace de descarga sigue siendo `/DetectorHojasCafe-v2.0.apk` con `download`; los textos de versión, el aviso y las cifras 99 % y 80 % están presentes; no aparece "App Store", "Google Play", "iPhone" ni analítica.
- El APK dentro de `public/` conserva sus 47 442 771 bytes.

### Cambios de texto

Ninguna cifra ni afirmación cambió. Se quitaron las etiquetas visibles "Paso 1/2/3" de "Cómo funciona" (las tres frases siguen iguales) y se añadieron textos alternativos a las dos capturas.

### NO EJECUTADO

- La página no se ha publicado en Vercel ni se ha probado la descarga desde un teléfono.
- El modo oscuro se revisó solo en escritorio.
- La carpeta de la página no está en git (incluye el APK de 47 MB).

## Modelo v3: arañita roja y ajustes de la app (2026-10-11)

**Estado: EN CURSO.** Los ajustes de la app están hechos; el modelo de cuatro clases tiene los datos preparados y falta entrenarlo en Colab.

### Ajustes de la pantalla de resultado (hechos)

- La palabra "Atrás" de la esquina superior izquierda se sustituyó por una flecha (`res/drawable/ic_arrow_back.xml`), con "Atrás" como descripción para lectores de pantalla.
- El botón "Nueva foto", que solo abría la cámara, se sustituyó por dos: "Tomar foto" y "Elegir de galería". Elegir de galería desde el resultado clasifica la imagen nueva sin salir de la pantalla.
- Comprobado en el emulador con la compilación de depuración: galería → resultado; "Elegir de galería" desde el resultado → resultado nuevo; flecha → inicio; "Tomar foto" desde el resultado → cámara. Sin cierres inesperados. Pruebas unitarias: 11 de 11.

### Arañita roja: datos (hechos)

- Nueva clase `arana_roja`. `CLASSES = ["arana_roja", "minador", "roya", "sana"]`, `MODEL_VERSION = "v3-2026-10"`.
- **Única fuente: RoCoLe** (`red_spider_mite`, 167 imágenes de café Robusta de Ecuador). Ni DECAFIA, ni BRACOL, ni JMuBEN tienen esta clase.
- `make data`: 3736 imágenes. Arañita roja: 152 tras quitar duplicados (108 train, 22 val, 22 test). Fugas: 0/0/0. Equilibrio por origen: correcto, desviación máxima 0.0105.
- Las copias con etiquetas contradictorias pasan de 11 a 35: hay fotos de RoCoLe repetidas con una etiqueta de arañita roja y otra distinta; se descartan todas, como fija la regla.
- Los resultados del modelo v2 se conservan en `ml/outputs/v2_final/`.

### Limitaciones que ya se conocen de esta clase

- Con una sola fuente no se puede medir cómo generaliza: no hay otro dataset con arañita roja para validarla ni para el conjunto final.
- 22 imágenes de test dan una cifra muy imprecisa.
- Son hojas de Robusta de un solo lugar; el modelo puede aprender rasgos de esas fotos y no de la plaga.

### NO EJECUTADO

- Entrenamiento del modelo v3, conversión, paridad y pruebas.
- Ficha de la arañita roja en la app (el texto ya está localizado en el informe, secciones 1.1.1.4 y 1.2.1.4).
- APK firmado y página de descarga con estos cambios.

## Modelo v3 — Entrenamiento, pruebas y versión 3.0 (2026-10-11)

**Estado: modelo v3 entrenado, probado en el teléfono y empaquetado. Sin publicar** (cambios confirmados en git local, pendientes de subir).

### Entrenamiento (Colab, Tesla T4)

- Paso de medición (`stage1_v3`, sin BRACOL): 1258 s, 10 + 21 épocas. Modelo final: 1671 s, 10 + 22 épocas. La sesión se cerró al terminar.
- Test interno del modelo final (556 imágenes): exactitud 0.9388, F1 macro 0.8611.

| Clase | Precisión | Recall | F1 | Imágenes |
|---|---|---|---|---|
| arana_roja | 0.5417 | 0.5909 | 0.5652 | 22 |
| minador | 0.9891 | 0.9785 | 0.9838 | 93 |
| roya | 0.9268 | 0.9360 | 0.9314 | 203 |
| sana | 0.9702 | 0.9580 | 0.9641 | 238 |

Matriz de confusión (filas = clase real; columnas = arana_roja, minador, roya, sana): `[13, 0, 6, 3]`, `[0, 91, 2, 0]`, `[8, 1, 190, 4]`, `[3, 0, 7, 228]`.

### Qué pasó con la arañita roja

- **Es una clase débil:** de 22 hojas con arañita roja, el modelo reconoce 13; y de 24 que llamó arañita roja, 13 lo eran.
- **Se confunde con roya y con hoja sana**, todas dentro de RoCoLe: 6 arañitas salen como roya, 8 royas como arañita.
- **Tuvo costo en RoCoLe:** la exactitud en esa fuente baja de 0.9847 (v2) a 0.8565 (v3); el recall de roya pasa de 0.9647 a 0.8554 y el de sana de 1.0000 a 0.9099.

### Qué pasó con las otras tres clases fuera de los datos

| Medida | v2 (3 clases) | v3 (4 clases) |
|---|---|---|
| BRACOL sin haberlo visto, F1 macro de 3 clases | 0.8494 | 0.8637 |
| JMuBEN, exactitud | 0.8003 | 0.8125 |
| JMuBEN, F1 macro de 3 clases | 0.7658 | 0.7806 |
| JMuBEN, recall minador | 0.5458 | 0.5722 |

- En los dos conjuntos externos las tres clases originales quedan iguales o algo mejor. La diferencia es pequeña y hay un solo entrenamiento por versión, así que no se puede afirmar que sea una mejora real.
- En JMuBEN, 96 hojas con minador se clasificaron como arañita roja (de 16 978).
- Con el umbral 0.60, en JMuBEN se acepta el 86.7 % de las imágenes, con exactitud 0.8528 sobre las aceptadas.

### Conversión, paridad y pruebas

- `model_fp32.tflite`: 16 077 592 bytes, salida `[1,4]`. Keras vs fp32: 100 % de coincidencia, diferencia máxima 0.00044.
- Vectores de referencia: 10 imágenes (2 arañita, 2 minador, 3 roya, 3 sana); el modelo acierta la clase real en 8.
- Unitarias: 11 de 11. Instrumentadas en el teléfono (Motorola Edge 30): todas en verde tras corregir la prueba de nivel 1, que asumía tres clases. Nivel 1: diferencia máxima 0.0000006. Nivel 2: 10 de 10. Latencia: mediana 48 ms.

### Versión 3.0 de la app

- Nombre **BioCafe**, flecha de retroceso, botones "Tomar foto" y "Elegir de galería" en el resultado, ficha de la arañita roja.
- APK firmado con la misma firma: `dist/BioCafe-v3.0.apk`, 47 465 559 bytes, sin `INTERNET`. Instalado en el teléfono y en el emulador: abre sin cierres inesperados. En el emulador, una hoja con roya da "Roya del café 87 %" y muestra la arañita roja entre las tres clases.
- Página de descarga actualizada: nombre, capturas nuevas, enlace a `BioCafe-v3.0.apk`, cuatro clases, cifras 94 % (interno) y 81 % (externo) y dos notas nuevas sobre la arañita roja. Compila; revisada en móvil y escritorio.
- `docs/resultados.md` regenerado con la comparación v1, v2 y v3.

### NO EJECUTADO

- Subir los cambios a GitHub y, con ello, publicar la página y el APK nuevos.
- Recorrido completo foto → resultado en el teléfono con la versión firmada (solo se comprobó que abre; el recorrido se hizo en el emulador).
- Prueba de la arañita roja con imágenes de otra fuente: no existe ninguna.
- Fotos de campo del humano (fase 12, paso 2).

## Búsqueda de más imágenes de arañita roja (2026-10-11)

**Resultado: no hay imágenes nuevas.** Los tres datasets públicos encontrados son copias de RoCoLe.

| Dataset (Roboflow Universe, CC BY 4.0) | Qué resultó ser | Cómo se comprobó |
|---|---|---|
| `coffee-leaf-detection/rocolem` (1490 imágenes) | Copia de RoCoLe | Conteos por clase casi idénticos a RoCoLe (757 sanas, 165 arañita roja); no se descargó |
| `coffee-leaf-detection/classifier-lubn1` (19 676 imágenes exportadas) | RoCoLe con aumento de datos | Los 19 676 archivos conservan nombres de RoCoLe (`C<n>P<n>H<n>` / `E<n>`) |
| `silvivision/red-spider-mite-9vj09` (6719 imágenes, 930 de arañita roja) | En arañita roja, 27 fotos originales repetidas unas 34 veces con aumento | 24 de las 27 coinciden por hash perceptual con arañitas de RoCoLe (distancia mediana 6) |

- El tercero también trae roya y minador sobre fondo blanco (parecidos a BRACOL y a Silva et al.) y "brown eye spot" (mancha de hierro) en campo; no se analizaron porque no eran el objetivo.
- Los buscadores de Zenodo y Mendeley Data rechazaron las consultas automáticas (HTTP 403 y 500): **esa parte quedó sin revisar**.
- Las descargas se borraron del equipo. La clave de Roboflow del humano está en `ml/data/roboflow_key.txt`, fuera de git.

Conclusión: con datos públicos, la arañita roja queda limitada a las 152 imágenes de RoCoLe. Mejorarla requiere fotos nuevas.

## Experimentos para mejorar la arañita roja (2026-10-11)

**Resultado: ninguna variante de entrenamiento mejora la arañita roja.** El límite está en los datos.

### Por qué y cómo

- La arañita roja acierta poco y se comprobó que no hay más imágenes públicas. Se probaron cambios de método.
- **Validación cruzada de 3 particiones** sobre las 3736 imágenes, por grupos (una planta o un grupo de casi duplicados nunca se reparte) y estratificada por origen y clase. Cada imagen se prueba exactamente una vez, así que la arañita roja se evalúa con 152 imágenes en lugar de 22.
- Todas las variantes se evalúan con la imagen completa aplastada al tamaño de entrada, como la envía la app. El recorte solo se usa al entrenar.
- Script: `ml/cv_experimentos.py`; pruebas: `ml/tests/test_cv_folds.py`. Resultados y predicciones imagen por imagen en `ml/outputs/cv/`.
- **Dónde se ejecutó: en el equipo local** (NVIDIA GeForce RTX 4050 Laptop, TensorFlow 2.21.0, Python 3.12.8), para agilizar. Son experimentos de exploración; el modelo que se entrega sigue siendo el entrenado en Colab.

### Variantes

| Variante | Configuración |
|---|---|
| Base | Receta actual: EfficientNet-B0, 224 px, lote 32, entropía cruzada con suavizado 0.1 |
| Recorte a la hoja | Como la base; al entrenar, con probabilidad 0.5 se recorta hacia el contorno de la hoja antes de reducir |
| Refuerzo | Pérdida focal (gamma 2) y peso doble para la arañita roja |
| Resolución 320 | Entrada de 320 px, lote 16 (el lote 32 no cabe en 6 GB) |
| Recorte + resolución | Las dos anteriores juntas |

Todas: hasta 6 épocas de cabeza y 25 de ajuste fino con parada temprana, semilla 42.

### Resultados (arañita roja, 152 imágenes probadas una vez)

| Variante | Recall | Precisión | F1 | IC 95 % del F1 | Exactitud general | Exactitud en RoCoLe | Tiempo |
|---|---|---|---|---|---|---|---|
| Base | 0.5658 | 0.5890 | 0.5772 | 0.508–0.639 | 0.9390 | 0.8727 | 759 s |
| Recorte a la hoja | 0.6053 | 0.5198 | 0.5593 | 0.491–0.622 | 0.9331 | 0.8582 | 722 s |
| Refuerzo | 0.7039 | 0.4672 | 0.5617 | 0.504–0.618 | 0.9221 | 0.8431 | 770 s |
| Resolución 320 | 0.6053 | 0.5542 | 0.5786 | 0.512–0.637 | 0.9419 | 0.8796 | 1364 s |
| Recorte + resolución | 0.5789 | 0.5570 | 0.5677 | 0.502–0.631 | 0.9416 | 0.8775 | 1085 s |

Intervalos por remuestreo (1000 repeticiones) de las predicciones agrupadas. La desviación del F1 entre particiones va de 0.036 a 0.073 según la variante.

### Lectura

- **El F1 queda entre 0.56 y 0.58 en las cinco.** Todos los intervalos se solapan casi por completo: las diferencias son indistinguibles del azar.
- **El error es siempre arañita roja contra roya.** En la base, 57 de 152 arañitas salen como roya y 51 royas salen como arañita; con minador y con hoja sana casi no se confunde (recall: minador 0.9744, sana 0.9781, roya 0.9185).
- **Los ajustes solo mueven el punto de corte.** El refuerzo sube el recall a 0.70, pero duplica las falsas alarmas (103 royas como arañita) y baja la exactitud general a 0.9221.
- **La mayor resolución no ayuda a la arañita roja.** Sube la exactitud general de 0.9390 a 0.9419, dentro del margen de azar, y cuesta más tiempo de cómputo.
- La validación cruzada confirma la cifra del test del modelo v3 (13 de 22): no era casualidad.

### Decisión

No se cambia la receta de entrenamiento. Se añadirá a la app una regla de "duda entre arañita roja y roya" (pendiente de calibrar con las probabilidades de la validación cruzada).

### NO EJECUTADO

- Control de tamaño de lote: las variantes de 320 px usan lote 16 y la base lote 32, así que no es una comparación pura de resolución. No se corrió la base con lote 16.
- Repetición con otras semillas. Se está corriendo una segunda vez la base, que servirá también para ver cuánto cambia el resultado entre ejecuciones idénticas.
- Arquitecturas más grandes y resoluciones mayores de 320.

## Regla de "duda entre arañita roja y roya" (2026-10-11)

**Estado: implementada y probada en el emulador. Sin publicar.**

### Qué hace

Cuando las dos clases más probables son arañita roja y roya y la diferencia entre sus probabilidades es menor de 0.40, la app no afirma una: muestra "Puede ser … o …", las dos posibilidades con su porcentaje y los síntomas de ambas. Esta comprobación va antes que el umbral general: nombrar a las dos candidatas es más útil que un "No se pudo determinar".

### Cómo se eligió el 0.40

- Con las probabilidades de la validación cruzada de la receta base (segunda corrida, 3736 imágenes; `ml/outputs/cv/regla_duda.json`).
- Al subir el margen, la precisión de lo que la app afirma como arañita roja pasa de 0.58 (sin regla) a 0.74 con 0.40, y a partir de ahí deja de mejorar mientras se siguen ocultando aciertos.
- Con 0.40 en la validación cruzada: 197 imágenes (5.3 %) pasan a "duda"; se evitan 77 errores y se ocultan 120 aciertos; en 190 de las 197 la clase real es una de las dos que se muestran.
- La segunda corrida de la base dio para la arañita roja recall 0.5921, precisión 0.5806 y F1 0.5863 (la primera, 0.5772): la misma receta varía cerca de 0.01 de F1 entre ejecuciones, y hasta 0.05 en una partición.

### Efecto en el modelo que se entrega (test interno, 556 imágenes)

| | Sin regla | Con regla |
|---|---|---|
| Respuestas de "duda" | 0 | 16 |
| De esas, errores evitados | | 7 |
| De esas, aciertos que quedan como duda | | 9 |
| Clase real entre las dos mostradas | | 16 de 16 |
| Veces que afirma "arañita roja" | 24 | 16 |
| Precisión al afirmar "arañita roja" | 0.5417 | 0.6875 |
| Precisión al afirmar "roya" | 0.9268 | 0.9468 |
| Exactitud de lo que afirma | 0.9388 | 0.9599 (524 imágenes) |

Otras 16 imágenes quedan por debajo del umbral 0.60 ("No se pudo determinar"). Detalle en `ml/outputs/final/regla_duda_modelo_final.json`.

### Qué se hizo en la app

- `DoubtRule` en `ClassifierLogic.kt`, leída de `threshold.json` (`"doubt": {"classes": ["arana_roja", "roya"], "margin": 0.4}`); `ClassificationResult.doubt`; pantalla `DoubtResult`.
- Pruebas unitarias escritas antes de implementar (fallaban al compilar; ahora 16 de 16 en verde): caso dudoso, ganador claro, pareja distinta, sin regla y lectura del archivo.
- Emulador, con el APK firmado: una hoja de arañita roja del test que el modelo daba como roya (57 % frente a 33 %) muestra ahora "Puede ser Roya del café o Arañita roja del café" con las dos fichas. Sin cierres inesperados.
- APK firmado regenerado (`dist/BioCafe-v3.0.apk`, 47 466 955 bytes) e instalado en el teléfono; copiado a la página de descarga.

### Límites

- **No mejora el modelo:** reparte de otra forma lo que ya sabe. El recall de la arañita roja como respuesta afirmada baja, porque parte de sus aciertos quedan como "duda".
- El margen se calibró con modelos de validación cruzada de la misma receta, no con el modelo entregado.
- Las cifras del modelo entregado son sobre 556 imágenes de las mismas fuentes; 16 casos de duda son pocos.

### NO EJECUTADO

- Pruebas instrumentadas tras este cambio (la regla no toca la inferencia; las de paridad se corrieron antes de añadirla).
- La pantalla de duda en el teléfono físico.

## Informe: secciones completadas (2026-10-11)

### Qué se hizo

- El informe (`docs/Protocolo de entrega del Documento final…docx`) tenía sin desarrollar los objetivos específicos 3 y 4 y las conclusiones, que conservaban el texto de la plantilla.
- Se generó una copia completada, `docs/Informe_BioCafe_completado.docx`. **El original no se modificó.**
- Contenido añadido: desarrollo del objetivo 3 (datos, entrenamiento con CUDA, integración en el móvil, alcance), desarrollo del objetivo 4 (prueba interna, conjunto externo, análisis de la arañita roja, tiempos y pruebas, limitaciones), conclusiones por objetivo, recomendaciones, cuatro tablas, cuatro imágenes (tres capturas de la app y la matriz de confusión) y seis referencias nuevas ([39] a [44]).
- Las cifras de las tablas se leen de `ml/outputs/`; el script que lo genera quedó en `docs/herramientas/completar_informe.py`.

### Qué se comprobó

- El archivo es un `.docx` válido como ZIP y su XML está bien formado; las 15 imágenes referenciadas existen; no queda texto de plantilla en las tres secciones reemplazadas.
- El texto nuevo se leyó completo en versión de texto plano.

### NO EJECUTADO

- **No se abrió en Word ni se convirtió a PDF** (no hay LibreOffice en el equipo): la maquetación, los saltos de página y el aspecto de tablas e imágenes están sin revisar.
- No se tocaron el índice ni las indicaciones de plantilla que quedan en la introducción.
- Las seis referencias nuevas están como texto; el informe exige que salgan de Zotero o Mendeley.

### Incoherencia que el humano debe resolver

La sección 2.4 del informe afirma que se entrena en la nube «debido a la falta de una unidad de procesamiento gráfico (GPU) física en el equipo de desarrollo local». El texto nuevo dice, porque es lo que ocurrió, que los experimentos de validación cruzada se ejecutaron en un equipo local con GPU NVIDIA. Una de las dos frases debe ajustarse.

## Informe: revisión de la maquetación (2026-10-13)

- Se convirtió `docs/Informe_BioCafe_completado.docx` a PDF con el conversor de OnlyOffice (instalado en el equipo) y se revisaron las 13 páginas que contienen el texto nuevo (34 a 46 de 46).
- **Bien alineado:** texto justificado dentro de los márgenes, objetivos 3 y 4 numerados a continuación del 1 y el 2, tablas e imágenes centradas y dentro del ancho de página, pies de figura centrados, referencias nuevas al final de la lista.
- **Corregido:** el encabezado «Sensibilidad» de la tabla de validación cruzada se partía en dos líneas; se ensanchó la columna.
- **Corregido, aunque venía del original:** el título «Conclusiones y recomendaciones» se partía dejando la «C» sola en una línea, por una sangría de primera línea heredada de la plantilla. Se igualó a la del título «Bibliografía».
- **Defecto del original, sin tocar:** el pie de página muestra un número fijo («1» en las primeras páginas y «10» en el resto) en lugar del número real, porque en la plantilla es texto y no un campo de numeración.
- Se añadió la versión PDF: `docs/Informe_BioCafe_completado.pdf`.
- No se comprobó en Microsoft Word; la conversión se hizo con OnlyOffice y puede haber diferencias menores.

## Póster actualizado con los objetivos 3 y 4 (2026-10-13)

- El póster original (`docs/Poster_Deteccion_Plagas_Cafe(1).pptx`) solo cubría los objetivos 1 y 2 y decía que quedaba por construir el sistema. Se generó una copia actualizada, `docs/Poster_BioCafe_actualizado.pptx` (y su PDF), con `docs/herramientas/ajustar_poster.py`. El original no se modificó.
- **Cambios:** el resumen y la fase de modelado reflejan lo construido; las cuatro tarjetas del objetivo 2 dicen lo que se eligió de verdad (EfficientNet-B0 frente a MobileNetV2, RoCoLe + DECAFIA + BRACOL con 3736 imágenes, Mask R-CNN sin implementar, CUDA en Colab y TensorFlow Lite en el teléfono); el flujo dice «Modelo EfficientNet-B0»; se añadió un bloque de objetivos 3 y 4 con tres capturas de la app (las mismas del informe) y tres cifras (94 %, 81 %, 48 ms); se reescribieron las conclusiones; se añadieron las referencias de BRACOL, RoCoLe y EfficientNet.
- Para hacer sitio se compactaron la tabla de viabilidad, las tarjetas y el flujo. No se cambió el diseño (colores, tipografía, encabezado, pie).
- **Cifras, todas de `ml/outputs/final/`:** exactitud interna 0,9388, exactitud en JMuBEN 0,8125, latencia mediana 48 ms, F1 de arañita roja 0,5652, F1 macro en BRACOL no visto 0,8494 frente a 0,7313.
- **Comprobado:** el archivo abre y se convierte a PDF con OnlyOffice; en el render no hay texto desbordado ni elementos solapados.
- **No comprobado:** no se abrió en Microsoft PowerPoint. Las fuentes pueden medir distinto y conviene revisar las tarjetas y las conclusiones antes de imprimir.
