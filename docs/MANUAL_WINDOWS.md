# Manual de instalación en Windows

Guía para abrir, compilar y modificar el proyecto en un PC con Windows 10 u 11.

> **Estado de esta guía:** el proyecto se desarrolló y probó en Linux. **Estos pasos no se han ejecutado en Windows.** Los comandos están adaptados a PowerShell y las versiones están verificadas, pero si algo falla, anota el error exacto y repórtalo.

## ¿Qué necesito instalar?

Depende de lo que vayas a hacer. La mayoría solo necesita la ruta A.

| Quiero… | Ruta | ¿Necesito Colab? | Tiempo aproximado |
|---|---|---|---|
| Abrir la app, cambiar pantallas o textos, compilar y probarla | **A** | **No** | 30–60 min (casi todo son descargas) |
| Ejecutar los scripts de datos, paridad o regenerar el informe de resultados | **A + B** | No | 1–2 h |
| Volver a entrenar el modelo | **A + B + C** | **Sí** | 2–3 h |

**Sobre Colab:** el modelo ya entrenado viene dentro del proyecto (`android/app/src/main/assets/model.tflite`). Solo hace falta Colab si se cambian los datos o el entrenamiento.

## Antes de empezar: cómo recibir el proyecto

El repositorio todavía no está publicado en GitHub, así que se comparte como carpeta comprimida.

Quien comparte debe incluir estas carpetas, que **no están en git** pero hacen falta:

| Carpeta o archivo | Para qué sirve | Sin esto… |
|---|---|---|
| `android/app/src/androidTest/assets/golden/` | Imágenes de referencia de las pruebas | Fallan las pruebas instrumentadas |
| `ml/outputs/golden/` | Las mismas imágenes, del lado de Python | No se puede comparar la paridad |
| `ml/outputs/model.keras` | Modelo en formato Keras | No se pueden repetir las fases 3 a 5 sin reentrenar |

Y debe **excluir** estas, que son pesadas o propias de cada equipo: `ml/.venv/`, `ml/data/`, `android/build/`, `android/app/build/`, `android/.gradle/` y `android/local.properties`.

Descomprime el proyecto en una ruta **corta y sin espacios ni tildes**, por ejemplo `C:\dev\cafe-detector`. Las rutas largas o con espacios dan problemas con Gradle en Windows.

---

## Ruta A. Abrir y modificar la app

### A1. Instalar las herramientas

| Herramienta | Enlace | Notas |
|---|---|---|
| Android Studio | https://developer.android.com/studio | Incluye el Android SDK, el emulador, `adb` y un JDK |
| Git (opcional) | https://git-scm.com/download/win | Solo para ver el historial o guardar cambios |

Instala Android Studio con las opciones por defecto. En el primer arranque, deja que el asistente descargue el SDK.

### A2. Instalar la plataforma Android que usa el proyecto

El proyecto compila contra **Android 17 (API 37)**.

1. En Android Studio: `More Actions` → `SDK Manager` (o `Tools` → `SDK Manager`).
2. Pestaña **SDK Platforms**: marca **Android 17.0 (API 37)**.
3. Pestaña **SDK Tools**: comprueba que estén marcados **Android SDK Build-Tools**, **Android SDK Platform-Tools** y **Android Emulator**.
4. Pulsa `Apply` y espera la descarga.

### A3. Abrir el proyecto

1. `File` → `Open` y elige la carpeta **`android`** (no la raíz del proyecto).
2. Espera a que termine la sincronización de Gradle. La primera vez descarga Gradle 9.8.1 y las librerías; puede tardar varios minutos y necesita internet.

Android Studio crea solo el archivo `android/local.properties` con la ruta del SDK.

**Si la sincronización falla con un error de versión de Java:** el proyecto se compiló con JDK 21. Instala Temurin 21 desde https://adoptium.net/ y selecciónalo en `File` → `Settings` → `Build, Execution, Deployment` → `Build Tools` → `Gradle` → `Gradle JDK`.

### A4. Crear un emulador

1. `Tools` → `Device Manager` → `+` → `Create Virtual Device`.
2. Elige un teléfono (por ejemplo `Medium Phone`) y una imagen de sistema **API 37, x86_64**.
3. Termina el asistente y arranca el dispositivo con el botón ▶.

La cámara del emulador muestra una sala virtual, no una hoja. Para probar con hojas reales, usa "Elegir de galería" con una foto copiada al emulador (arrastra el archivo a la ventana del emulador) o conecta un teléfono.

### A5. Ejecutar la app

Pulsa ▶ `Run 'app'`. La app se instala y abre en el emulador.

### A6. Comprobar que todo funciona

En el panel `Terminal` de Android Studio (queda en la carpeta `android`):

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug
```

Resultado esperado: `BUILD SUCCESSFUL`, 11 pruebas unitarias sin fallos y el APK en `app\build\outputs\apk\debug\app-debug.apk`.

Con el emulador encendido y la carpeta `golden` en su sitio:

```powershell
.\gradlew.bat connectedDebugAndroidTest
```

Resultado esperado: 9 pruebas instrumentadas sin fallos.

**Si `gradlew.bat` dice que no encuentra Java:** en esa terminal, ejecuta primero

```powershell
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
```

### A7. Dónde tocar según lo que quieras cambiar

Todo está bajo `android\app\src\main\`.

| Quiero cambiar… | Archivo |
|---|---|
| Un texto de la interfaz | `res\values\strings.xml` |
| Colores | `java\...\ui\Theme.kt` |
| Pantalla de inicio, cámara o resultado | `java\...\ui\HomeScreen.kt`, `CameraScreen.kt`, `ResultScreen.kt` |
| Las fichas de roya y minador | `assets\conditions.json` |
| El umbral de confianza | `assets\threshold.json` |
| Cómo se prepara la imagen o se llama al modelo | `java\...\ml\ImageUtils.kt`, `CoffeeLeafClassifier.kt` |

Reglas del proyecto que no deben romperse:

- La app **no normaliza** la imagen: el modelo lo hace por dentro.
- No se añade el permiso `INTERNET`.
- Los textos de las fichas salen del informe; no se añaden recomendaciones de fungicidas ni dosis.

---

## Ruta B. Ejecutar los scripts de Python

Necesaria para preparar datos, repetir la paridad o regenerar `docs/resultados.md`.

### B1. Instalar `uv`

`uv` instala Python y las librerías. En PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra y vuelve a abrir PowerShell. Documentación: https://docs.astral.sh/uv/

### B2. Crear el entorno

Desde la raíz del proyecto:

```powershell
uv venv --python 3.12 ml\.venv
uv pip install --python ml\.venv\Scripts\python.exe -r ml\requirements.txt
```

Se usa Python 3.12 porque TensorFlow 2.21.0 solo existe para Python 3.10 a 3.13.

**En Windows, TensorFlow corre solo en CPU.** Sirve para preparar datos, convertir el modelo y comprobar la paridad. Para entrenar, usa Colab (ruta C).

### B3. Ejecutar los scripts

El proyecto usa un `Makefile`, que no funciona en Windows sin herramientas extra. Ejecuta los scripts directamente:

```powershell
cd ml
.\.venv\Scripts\python.exe 01_preparar_datos.py      # equivale a: make data
.\.venv\Scripts\python.exe 03_evaluar.py             # make eval
.\.venv\Scripts\python.exe 04_convertir_tflite.py    # make tflite
.\.venv\Scripts\python.exe 05_paridad_tflite.py      # make parity
.\.venv\Scripts\python.exe generar_resultados.py     # make results
```

Qué necesita cada uno:

| Script | Necesita |
|---|---|
| `01_preparar_datos.py` | Los datasets descargados (paso B4) |
| `03`, `04`, `05` | `ml\outputs\model.keras` y los datos preparados |
| `generar_resultados.py` | Solo los archivos de `ml\outputs\` (ya vienen en el proyecto) |

### B4. Descargar los datasets (solo si vas a preparar datos)

Ocupan unos 900 MB comprimidos. No se incluyen en el proyecto.

| Dataset | Enlace | Archivos que hay que bajar |
|---|---|---|
| RoCoLe | https://data.mendeley.com/datasets/c5yvn32dzg/2 | `RoCoLe-voc.tar.gz` y `RoCoLE-json.json` |
| DECAFIA | https://zenodo.org/records/19931904 | `CoffeeLeaf-CO.zip` |

Colócalos y descomprímelos así (desde la raíz del proyecto):

```powershell
mkdir ml\data\raw\rocole, ml\data\raw\decafia
# copia aquí los tres archivos descargados y luego:
tar -xzf ml\data\raw\rocole\RoCoLe-voc.tar.gz -C ml\data\raw\rocole
Expand-Archive ml\data\raw\decafia\CoffeeLeaf-CO.zip -DestinationPath ml\data\raw\decafia
```

Debe quedar esta estructura:

```
ml\data\raw\rocole\RoCoLE-json.json
ml\data\raw\rocole\export\*.jpeg
ml\data\raw\decafia\CoffeeLeaf-CO\images\...
ml\data\raw\decafia\CoffeeLeaf-CO\labels\...
```

---

## Ruta C. Volver a entrenar en Google Colab

Solo si cambias los datos o el entrenamiento. Necesitas una cuenta de Google.

> El entrenamiento original se lanzó desde Linux con la CLI de Colab, que **no funciona en Windows**. En Windows se usa el cuaderno desde el navegador. **El cuaderno no se ha probado en el navegador**; hace los mismos pasos que el proceso que sí se ejecutó.

### C1. Preparar el paquete de código

Desde la raíz del proyecto, con el entorno de la ruta B:

```powershell
ml\.venv\Scripts\python.exe -m zipfile -c cafe_ml_bundle.zip ml/config.py ml/requirements.txt ml/01_preparar_datos.py ml/02_entrenar.py ml/03_evaluar.py ml/04_convertir_tflite.py ml/05_paridad_tflite.py ml/colab_run.py
```

Usa las barras `/` tal como están: Colab es Linux y necesita esas rutas dentro del zip.

### C2. Ejecutar el cuaderno

1. Abre https://colab.research.google.com/ → `Archivo` → `Subir cuaderno` → elige `ml\colab_entrenamiento.ipynb`.
2. `Entorno de ejecución` → `Cambiar tipo de entorno de ejecución` → **GPU T4**.
3. Ejecuta las celdas **en orden**. La primera pide subir `cafe_ml_bundle.zip`.
4. Cada fase termina con una línea `ACEPTACIÓN FASE N: OK`. Si una celda falla, **no sigas**: copia el error.
5. La última celda descarga `cafe_outputs.zip`.

Duración de referencia: el entrenamiento tardó unos 17 minutos en una T4, más las descargas de los datasets.

### C3. Llevar el modelo nuevo a la app

Descomprime `cafe_outputs.zip` y, desde la raíz del proyecto:

```powershell
Expand-Archive cafe_outputs.zip -DestinationPath ml -Force
Copy-Item ml\outputs\model_fp32.tflite android\app\src\main\assets\model.tflite
Copy-Item ml\outputs\labels.txt, ml\outputs\threshold.json android\app\src\main\assets\
Copy-Item ml\outputs\golden\* android\app\src\androidTest\assets\golden\
ml\.venv\Scripts\python.exe ml\generar_resultados.py
```

La app usa el modelo **sin cuantizar** (`model_fp32.tflite`); el motivo está en `docs/decisiones.md`.

Después repite el paso A6: las pruebas deben seguir en verde con el modelo nuevo.

---

## Lista de comprobación

- [ ] Android Studio abre la carpeta `android` y la sincronización de Gradle termina sin errores.
- [ ] `.\gradlew.bat testDebugUnitTest assembleDebug` termina con `BUILD SUCCESSFUL`.
- [ ] La app abre en el emulador y muestra "Detector de hojas de café".
- [ ] "Elegir de galería" con una foto de hoja lleva a la pantalla de resultado.
- [ ] (Si copiaste `golden`) `.\gradlew.bat connectedDebugAndroidTest` pasa las 9 pruebas.

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `SDK location not found` | Falta `android\local.properties` | Abre el proyecto con Android Studio, que lo crea |
| Error de sincronización que menciona `compileSdk 37` o una plataforma no encontrada | Falta la plataforma API 37 | Paso A2 |
| Error de versión de Java al sincronizar | JDK no compatible | Instala Temurin 21 y selecciónalo (paso A3) |
| Fallan las pruebas instrumentadas con `FileNotFoundException: golden/...` | No se copió la carpeta `golden` | Pídela a quien compartió el proyecto |
| `No matching distribution found for tensorflow==2.21.0` | Python 3.14 u otra versión no admitida | Usa `--python 3.12` (paso B2) |
| El emulador clasifica una sala como "Hoja sana" | La cámara del emulador no muestra una hoja y el modelo solo conoce hojas | Es una limitación conocida; prueba con fotos desde la galería |

## Para saber más

- `README.md`: resumen y reproducción en Linux.
- `docs/resultados.md`: métricas y limitaciones del modelo.
- `docs/bitacora.md` y `docs/decisiones.md`: qué se hizo en cada fase y por qué.
