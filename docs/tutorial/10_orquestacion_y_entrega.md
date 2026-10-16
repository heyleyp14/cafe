# Capítulo 10: Orquestación y entrega

Cómo se encadenan los pasos, cómo se generan los informes y cómo llega el APK al usuario.

## ¿Por qué existe?

Ya conocemos todas las máquinas de la fábrica. Falta la **línea de empaque**: quién decide el orden en que funcionan, cómo se lleva el trabajo a otra planta (Colab) y se trae de vuelta, cómo se redacta el reporte de calidad sin errores de copia, y cómo sale el producto final (un APK firmado) hacia el cliente (una página de descarga).

Sin esta parte, cada paso dependería de la memoria de quien lo ejecuta, y las cifras del informe podrían no coincidir con las de los archivos.

## La idea principal

- Un **Makefile** da un nombre corto a cada paso del pipeline de Python.
- Dos **zip** llevan el código y los datos preparados a Google Colab, donde `colab_run_v3.py` entrena sin supervisión.
- Un script, **`generar_resultados.py`**, escribe `docs/resultados.md` leyendo solo los JSON de `ml/outputs/`: ninguna cifra se escribe a mano.
- **Gradle** compila la app y firma la versión de distribución.
- Una página **Next.js** ofrece el APK para descargar.

## Cómo funciona en este código

Vive en:
- `Makefile`, `README.md`
- `ml/crear_bundle.py`, `ml/colab_run_v3.py`, `ml/generar_resultados.py`
- `docs/resultados.md`
- `android/app/build.gradle.kts`
- `docs/landing-detector-hojas-cafe/app/page.tsx` y `components/landing/{hero,performance}.tsx`
- `docs/COMO_SE_CONSTRUYO.md` (explicación sin código del mismo recorrido)

### El Makefile: un atajo por paso

```make
data:
	cd ml && $(PYTHON) 01_preparar_datos.py

train:
	cd ml && $(PYTHON) 02_entrenar.py --run $(RUN)
...
results:
	cd ml && $(PYTHON) generar_resultados.py
```

Los objetivos son `data`, `train`, `eval`, `tflite`, `parity`, `results`, `colab-bundle` y `colab-data`. La variable `RUN` (por defecto `final`) elige la carpeta `ml/outputs/$(RUN)/` donde trabaja cada paso. El Makefile también añade al `LD_LIBRARY_PATH` las librerías de CUDA que instala pip, porque TensorFlow no las encuentra solo.

### Ir y volver de Colab

`ml/crear_bundle.py` arma dos archivos:

```python
def create_data_bundle():
    """Only data/processed and the stats: never raw, external or final holdout images."""
```

- `cafe_ml_bundle.zip`: solo el código.
- `cafe_data_v2.zip`: las imágenes procesadas y `dataset_stats.json`. **Nunca** las imágenes crudas ni el conjunto final JMuBEN, que así no puede colarse por accidente en el entrenamiento.

En Colab, `colab_run_v3.py` instala las dependencias fijadas, comprueba que haya GPU, ejecuta `stage1_v3` y `final` ([capítulo 3](03_entrenamiento.md)) y comprime los resultados en `cafe_outputs_v3.zip`. El `README.md` describe el regreso: copiar `outputs/final/`, correr `make tflite parity`, copiar `model_fp32.tflite` a `android/app/src/main/assets/model.tflite` junto con `labels.txt` y `threshold.json`, copiar las imágenes golden a las pruebas y ejecutar `make results`.

### Un informe que no se escribe a mano

```python
"""Builds docs/resultados.md from the JSON files under ml/outputs so no figure is typed by hand.
```

`generar_resultados.py` lee `metrics.json`, `final_holdout.json`, `parity.json`, `threshold_source.json`, los resultados del teléfono y las corridas de la etapa 1, y arma las tablas de `docs/resultados.md`. El encabezado del informe lo advierte: "Archivo generado ... No editar a mano." Esto materializa la regla 3 del plan: "Nunca inventes resultados." Por la misma razón, la sección de resultados en campo dice "NO EJECUTADO": faltan fotos reales tomadas por el equipo.

### Compilar y firmar el APK

`android/app/build.gradle.kts` lee la firma de un archivo que nunca se sube a git:

```kotlin
// Release signing comes from android/keystore.properties, which is never versioned.
// Without that file the release build stays unsigned.
val keystoreFile = rootProject.file("keystore.properties")
```

La versión actual es `versionCode = 3`, `versionName = "3.0"`. `docs/decisiones.md` explica por qué el identificador sigue siendo `co.edu.unipamplona.cafedetector`: para que la versión nueva se instale encima de la anterior con la misma firma. Y advierte que sin ese almacén de claves no se pueden publicar actualizaciones compatibles.

### La página de descarga

La página está en `docs/landing-detector-hojas-cafe/`, hecha con Next.js. `app/page.tsx` solo compone secciones:

```tsx
<Hero />
<HowItWorks />
<div className="grid ...">
  <Install />
  <Performance />
  <Limitations />
  <Privacy />
</div>
```

`hero.tsx` enlaza el archivo `/BioCafe-v3.0.apk` e indica "Versión 3.0 · 47 MB · Android 8.0 o superior". `performance.tsx` muestra dos cifras redondeadas: 94 % de exactitud en imágenes de los mismos conjuntos del entrenamiento y 81 % en un conjunto externo nunca visto, que corresponden a 0.9388 y 0.8125 de `docs/resultados.md`. La sección de privacidad repite lo que garantiza el manifiesto: sin permiso de internet, solo cámara.

## Cómo se conecta

- **Ejecuta en Colab** el [entrenamiento](03_entrenamiento.md) y la [evaluación](04_evaluacion_umbral_y_duda.md).
- Encadena la [conversión y paridad](05_conversion_y_paridad.md) y copia sus archivos a los *assets* de la app.
- **Empaqueta en el APK** el [clasificador](06_clasificador_en_el_telefono.md), [el ViewModel](08_estado_y_navegacion.md) y [las pantallas](09_las_pantallas.md).

## Resumen

El Makefile ordena el pipeline, los zip llevan el trabajo a Colab y lo traen de vuelta, `generar_resultados.py` produce un informe sin cifras escritas a mano, Gradle firma el APK con una clave fuera de git y una página Next.js lo ofrece para descargar. Con esto ha recorrido BioCafe de punta a punta: de la foto en un dataset público a la respuesta prudente en el teléfono. Si algún término quedó oscuro, consulte el glosario.

Ver también: [Glosario](glosario.md)
