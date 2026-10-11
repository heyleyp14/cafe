# Registro de decisiones

Formato: fecha, decisión, motivo. Las marcadas **DECISIÓN** en el plan usan el valor por defecto salvo indicación contraria.

## 2026-10-10 — Raíz del repositorio

- **Decisión:** el directorio de trabajo actual (`proyecto/`) es la raíz del repositorio; no se crea una subcarpeta `cafe-detector/`.
- **Motivo:** el plan ya vive en esta carpeta y la instrucción del humano referencia `docs/bitacora.md` relativo a ella.

## 2026-10-10 — Alcance de la v1 (plan 1.3, valor por defecto)

- **Decisión:** clases `minador`, `roya`, `sana` (orden alfabético, fijo en `ml/config.py`).
- **Motivo:** es lo que RoCoLe y DECAFIA permiten sin recolectar datos nuevos.

## 2026-10-10 — Significado de "coco" en DECAFIA

- **Decisión:** la clase `coco` de DECAFIA **no** se mapea a ninguna clase de la v1.
- **Motivo:** el registro de Zenodo la define como "Curculionidae weevil defoliation" (defoliación por gorgojos), que no es roya, minador ni hoja sana. Las imágenes cuya clase dominante sea `coco` se tratarán con la regla de la fase 1 (descartar si no hay clase de la v1 dominante).
- **Fuente:** https://zenodo.org/records/19931904

## 2026-10-10 — Licencias y condiciones de uso de los datasets

| Dataset | Fuente verificada | Licencia | Condición |
|---|---|---|---|
| RoCoLe v2 (Parraga-Alava et al., 2019) | API pública de Mendeley Data, DOI `10.17632/c5yvn32dzg.2` | CC BY 4.0 | Atribución, enlace a la licencia e indicar cambios |
| DECAFIA / CoffeeLeaf-CO (Rosas Ruiz, Salom Medina, Barrero Perez, 2026) | API de Zenodo, DOI `10.5281/zenodo.19931904` | CC BY 4.0 | Atribución, enlace a la licencia e indicar cambios |

- **Decisión:** se citan ambos en el README y en "Acerca de" de la app. Aunque CC BY 4.0 permite redistribuir, **no se suben imágenes al repositorio** (regla del plan); `ml/data/` está en `.gitignore`.
- **Nota:** DECAFIA redistribuye material de terceros también bajo CC BY 4.0: RoCoLe (prefijo `SANAS_ROCOLE_*`) y Silva et al. 2020, DOI `10.17632/vfxf4trtcg.5` (prefijo `MINEIRO_*`). Silva et al. debe citarse también.

## 2026-10-10 — Riesgo de fuga entre datasets (a resolver en fase 1)

- **Hallazgo:** DECAFIA incluye hojas sanas de RoCoLe re-anotadas (`SANAS_ROCOLE_*`). Si se combinan ambos datasets sin más, la misma foto puede aparecer dos veces y caer en particiones distintas.
- **Decisión:** la deduplicación por hash de la fase 1 se hará **entre datasets y antes de dividir**, no solo dentro de cada uno.
- **Hallazgo:** DECAFIA trae su propia partición (1934/549/286). El plan exige 70/15/15 estratificado con semilla fija, así que se ignora la partición original y se vuelve a dividir.

## 2026-10-10 — Fase 1: reglas de etiquetado (plan, DECISIÓN de clase dominante)

- **RoCoLe:** `healthy` → `sana`; `rust_level_1..4` → `roya`; `red_spider_mite` (arañita roja) se descarta porque no es clase de la v1.
- **DECAFIA:** se cuentan las instancias de `roya`, `coco` y `minador` (la clase `hojas` es solo el contorno de la hoja y no cuenta). Sin instancias de enfermedad → `sana`. Con instancias → clase con más instancias; si esa clase es `coco`, se descarta; si hay empate, se descarta.
- **Motivo:** es la regla por defecto del plan. Se incluye `coco` en el conteo para no etiquetar como `roya` una hoja cuyo daño principal es otro.

## 2026-10-10 — Fase 1: exclusiones de DECAFIA por procedencia

- **Decisión:** se excluyen las imágenes `SANAS_ROCOLE_*` (454).
- **Motivo:** DECAFIA las declara derivadas de RoCoLe. Solo una parte se detecta por hash (están rotadas, reflejadas o reescaladas), así que conservarlas dejaría la misma hoja en particiones distintas. Los originales ya entran por RoCoLe, con su identificador de planta.
- **Decisión REVERTIDA el 2026-10-10 por instrucción del humano (ceñirse al plan):** se habían excluido los recortes `COCO_RECORTE_*`, `MINADO_RECORTES_*` y `ROYA_RECORTES_*`. Ya no se excluyen; pasan por la regla de clase dominante como cualquier otra imagen.
- **Motivo:** son acercamientos de la lesión, no hojas completas. No corresponden a la entrada de la app (una hoja completa) y podrían ser recortes de fotos presentes en otra partición, algo que un hash no detecta. Ese riesgo queda anotado como limitación en la bitácora.

## 2026-10-10 — Fase 1: duplicados y agrupación

- **Decisión:** hash perceptual dHash de 256 bits, comparado sobre las 8 orientaciones (rotaciones y espejos) de cada imagen, además de MD5.
  - Distancia ≤ 40: se considera la misma foto y se conserva una sola copia (la de RoCoLe si existe). Si las copias tienen etiquetas distintas, se descartan todas.
  - Distancia 41–52: se conservan, pero se obligan a caer en la misma partición.
- **Motivo:** los umbrales se eligieron mirando pares de muestra por distancia. Hasta ~45 los pares eran la misma foto (a menudo rotada); a partir de ~53 eran hojas distintas sobre fondo blanco o tomas distintas de una misma hoja, que el hash no puede unir (limitación anotada en la bitácora). Un primer intento con dHash de 64 bits daba falsos duplicados y se desechó.
- **Decisión:** las fotos de RoCoLe de la misma planta (`C<cultivo>P<planta>` en el nombre) van juntas a una sola partición.
- **Decisión:** se ignora la partición original de DECAFIA y se divide de nuevo 70/15/15 con semilla 42, estratificado por clase y respetando los grupos.

## 2026-10-10 — Entorno de entrenamiento

- **Decisión:** el entrenamiento y las cifras del informe se obtienen en Google Colab o Kaggle con GPU, como indica la sección 2 del plan.
- **Motivo:** instrucción del humano de ceñirse totalmente al plan. Se había preparado la GPU local (RTX 4050) sin que el plan lo pidiera; queda solo para pruebas de humo de los scripts.

## 2026-10-10 — Desviación pendiente de confirmar: `SANAS_ROCOLE_*`

- **Estado:** se mantiene la exclusión de las 454 imágenes `SANAS_ROCOLE_*` de DECAFIA, que el plan no menciona de forma literal.
- **Motivo:** el plan exige que ninguna imagen esté en dos particiones y que las fotos de una misma planta vayan juntas. Estas imágenes son copias transformadas de RoCoLe que el hash solo detecta en parte, así que incluirlas rompería ese criterio. Si el humano prefiere la lectura literal, se quita la constante `DECAFIA_DERIVED_PREFIXES`.

## 2026-10-10 — Fase 6: librería de inferencia y versiones

- **Decisión:** LiteRT `com.google.ai.edge.litert:litert:2.3.0` en todo el proyecto, con el import `org.tensorflow.lite.Interpreter`.
- **Motivo:** es la primera opción del plan. Se inspeccionó el AAR 2.3.0: la clase que contiene es `org.tensorflow.lite.Interpreter` (no `com.google.ai.edge.litert.Interpreter`, que el plan da como ejemplo), así que ese es el import válido para esta versión.
- **Decisión:** no se usa `litert-support`; el modelo se cargará con `assets.openFd` + `FileChannel.map`, una de las dos opciones que da el plan.
- **Decisión:** versiones tomadas de Google Maven y Maven Central el 2026-10-10 (`android/gradle/libs.versions.toml`): AGP 9.4.1, Kotlin 2.4.21, Compose BOM 2026.09.00, CameraX 1.6.2, Lifecycle 2.11.0, Navigation 2.10.2, kotlinx-serialization-json 1.11.0, Gradle 9.8.1.
- **Decisión:** `compileSdk` y `targetSdk` 37 (la única plataforma instalada), `minSdk` 26 como pide el plan. Se compila con JDK 21 (el plan menciona JDK 17; el JDK 21 instalado funciona con AGP 9.4.1).

## 2026-10-10 — Modelo que se entrega en la app: fp32 (decisión del humano)

- **Decisión:** la app lleva el modelo **sin cuantizar** (`model_fp32.tflite`, copiado a `assets/` como `model.tflite`). Lo fija `APP_MODEL_FILE` en `ml/config.py`.
- **Motivo:** el plan pide a la vez cuantización de rango dinámico (fase 4) y diferencia de probabilidad < 0.01 entre Android y Python (fase 11). Con el modelo cuantizado esa prueba falla en 2 de 10 imágenes (0.0138 y 0.0152), porque sus resultados dependen de la CPU. El humano eligió la opción más exacta.
- **Qué cambia respecto al plan:** la fase 4 sigue generando los dos archivos, pero el que se usa es el fp32. Costo: 8.9 MB en lugar de 2.5 MB.
- **Consecuencia:** `probs_tflite` de `golden.json` se calcula ahora con el modelo fp32, que es el que ejecuta la app.

## 2026-10-10 — Fase 11, nivel 2: contra qué se compara la clase

- **Decisión:** la clase obtenida en Android con el `.jpg` se compara con la clase que predice TFLite en Python (el máximo de `probs_tflite`), no con la etiqueta real.
- **Motivo:** el nivel 2 es una prueba de paridad del flujo completo; la exactitud frente a la etiqueta real ya se mide en la fase 3.

## 2026-10-10 — Fase 10: permisos, hilos y delegado GPU

- **Decisión:** se quitan del manifiesto, con `tools:node="remove"`, los permisos que añaden las dependencias de LiteRT 2.3.0: `ACCESS_NETWORK_STATE`, `WAKE_LOCK`, `RECEIVE_BOOT_COMPLETED`, `FOREGROUND_SERVICE` y `FOREGROUND_SERVICE_DATA_SYNC`.
- **Motivo:** la app no usa red ni tareas en segundo plano; el plan exige que no haya `INTERNET` y una app sin conexión no debería declarar permisos que no necesita. Tras quitarlos, todas las pruebas y el flujo de la app siguen funcionando. Es una decisión propia, compatible con el plan y reversible.
- **Decisión:** se mantiene `setNumThreads(4)`, el valor del código del plan.
- **Motivo:** en el emulador la comparación 2 vs 4 hilos no es concluyente (ver bitácora); se decide con un teléfono real en la fase 12.
- **Decisión:** no se adopta el delegado GPU.
- **Motivo:** el plan lo marca como opcional y no se probó.

## 2026-10-10 — Validación externa con BRACOL (a petición del humano)

- **Decisión:** se añade una prueba con un dataset externo descargado de internet, **BRACOL** (Krohling, Esgario y Ventura; Mendeley Data `10.17632/yy2k5y8mxg.1`, CC BY 4.0).
- **Motivo:** el humano pidió no tomar él las fotos y usar imágenes de internet. Se eligió un dataset con etiquetas de sus autores en lugar de imágenes sueltas de la web, cuyas etiquetas no se pueden verificar.
- **Qué NO es:** no sustituye el paso 2 de la fase 12 (fotos reales tomadas por el humano en condiciones de campo), que sigue sin ejecutarse.
- **Reglas aplicadas:** subconjunto `leaf`; `predominant_stress` 0 → `sana`, 1 → `minador`, 2 → `roya`. Se excluyen 3 (phoma), 4 (cercospora) y 5 (sin documentar en el CSV), que no son clases de la v1. La codificación 1 y 2 se comprobó contra las columnas `miner` y `rust` del propio CSV.
- **Independencia:** ninguna imagen coincide por MD5 con los datos de entrenamiento; las más parecidas por hash perceptual (distancia ≥ 40) se revisaron a la vista y son hojas distintas.
- **Limitación del archivo:** el zip publicado está truncado en origen (el tamaño y el SHA-256 descargados coinciden con los que declara Mendeley, pero le falta el final). Se recuperaron 1402 de las 1747 imágenes; de las tres clases usadas quedaron 860.

## 2026-10-10 — Reentrenamiento v2: datos y evaluación (R1 y R2)

- **Decisión:** el reparto 70/15/15 se estratifica por **origen y clase** (por ejemplo `rocole/roya`), respetando los grupos. Una prueba automática (`ml/tests/test_split.py`) y una comprobación dentro del script lo verifican.
- **Motivo:** corregir el sesgo de la v1, donde RoCoLe era el 67 % del entrenamiento y cerca del 3 % de validación y test.
- **Decisión:** se añade BRACOL como tercera fuente (`predominant_stress` 0 → `sana`, 1 → `minador`, 2 → `roya`).
- **Decisión:** para BRACOL los duplicados se detectan **solo por MD5**, no por hash perceptual.
- **Motivo:** con los umbrales calibrados para RoCoLe y DECAFIA, el hash perceptual marcaba como duplicadas 419 de las 860 imágenes de BRACOL. Revisadas a la vista las parejas más cercanas, eran hojas distintas: el hash solo capta la silueta de una hoja centrada sobre fondo liso. **Costo:** la comprobación perceptual de fugas ya no cubre los pares con BRACOL; si BRACOL tuviera varias tomas de una misma hoja, no se detectarían.
- **Decisión:** las imágenes procesadas se guardan reducidas a 512 px de lado mayor (sin ampliar, conservando la proporción). Los hashes se siguen calculando sobre los originales.
- **Motivo:** permite subir los datos ya preparados a Colab. El modelo sigue recibiendo la imagen aplastada a 224×224, como fija el contrato.
- **Decisión:** selección de modelo en dos etapas. Etapa 1: entrenar con RoCoLe y DECAFIA y medir en BRACOL como fuente no vista. Etapa 2: reentrenar la arquitectura elegida con las tres fuentes y evaluarla una sola vez en JMuBEN.
- **Decisión:** el desbalance se corrige con pesos por muestra según su estrato (origen y clase), en lugar de `class_weight`.
- **No implementado:** sustitución de fondo en el aumento de datos (requiere segmentar la hoja, y el diagnóstico R0 mostró que el fondo no es la causa principal).

## 2026-10-11 — Modelo v2: arquitectura, umbral y congelación antes del conjunto final

- **Decisión:** el modelo v2 es **EfficientNet-B0**, entrenado con las tres fuentes (RoCoLe, DECAFIA y BRACOL).
- **Motivo:** en la etapa 1, sin haber visto BRACOL, obtuvo F1 macro 0.8494 en BRACOL frente a 0.7313 de MobileNetV2. Cambia el modelo base del plan original (MobileNetV2).
- **Decisión:** umbral de confianza **0.55**.
- **Motivo:** es el que dio la regla del plan aplicada a EfficientNet-B0 sobre una fuente no vista (etapa 1). El modelo final se entrena con todas las fuentes, así que ya no queda una fuente no vista para elegirlo; con la validación interna la regla da 0.40, que lo acepta todo. El origen del valor queda en `ml/outputs/final/threshold_source.json`.
- **Decisión:** la app sigue llevando el modelo sin cuantizar (`model_fp32.tflite`), ahora de 16 072 468 bytes.
- **Congelación:** modelo, umbral y código quedan confirmados en git **antes** de abrir el conjunto final (JMuBEN). Lo que se mida en él no se usa para cambiar nada.

## 2026-10-11 — Versión instalable: ícono y firma

- **Decisión:** ícono adaptativo vectorial (hoja dentro de las esquinas del marco guía, sobre el verde de la app). Copia para web en `docs/icono-app.svg`.
- **Decisión:** el APK de distribución es la compilación `release`, firmada con un almacén de claves nuevo creado para este proyecto. `versionName` 2.0, `versionCode` 2.
- **Dónde está la firma:** `android/cafe-detector-release.jks` y `android/keystore.properties` (contraseña generada al azar). **Ninguno de los dos está en git.** Hay que guardar copia: sin ese almacén no se pueden publicar actualizaciones que se instalen encima de esta versión.
- **Dónde está el APK:** `dist/DetectorHojasCafe-v2.0.apk` (fuera de git).
- **Nota:** una compilación de depuración y una de `release` tienen firmas distintas; para pasar de una a otra en el mismo teléfono hay que desinstalar primero.

## 2026-10-11 — Publicación en GitHub

- **Decisión del humano:** subir el proyecto completo al repositorio privado `josuerangel2005/cafe`, en la rama `main`.
- **Qué se versionó por esa instrucción** y antes estaba fuera: la página de descarga (con el APK de 47 MB), la maqueta de v0, el informe en Word, las 10 imágenes de referencia de las pruebas y `ml/outputs/final/model.keras`. Las imágenes de referencia son de los datasets (CC BY 4.0, citados en el README); el plan original pedía no redistribuir imágenes, y el humano decidió incluirlas.
- **Qué sigue fuera:**
  - Los datasets (`ml/data/`, unos 5 GB): varios archivos superan el límite de 100 MB por archivo de GitHub. Se descargan de sus fuentes.
  - El almacén de claves de la firma y su contraseña (`android/cafe-detector-release.jks`, `android/keystore.properties`): pendiente de confirmación del humano; el plan original prohíbe subir claves a git.
