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

## Antes de empezar: obtener el proyecto y saber qué falta

### Obtener el proyecto

El código está en GitHub, en un repositorio **privado**: https://github.com/josuerangel2005/cafe

1. Pide al dueño del repositorio que te invite como colaborador (`Settings` → `Collaborators` en GitHub) y acepta la invitación.
2. Instala Git (https://git-scm.com/download/win).
3. En PowerShell, en una ruta **corta y sin espacios ni tildes** (por ejemplo `C:\dev`):

```powershell
git clone https://github.com/josuerangel2005/cafe.git
cd cafe
```

Las rutas largas o con espacios dan problemas con Gradle en Windows.

### Qué NO viene en el repositorio

Esto es lo que tienes que conseguir o generar tú. Solo necesitas lo que corresponda a tu ruta.

| Qué falta | Por qué no está | Lo necesitas para | Cómo conseguirlo |
|---|---|---|---|
| Datasets de entrenamiento (unos 900 MB comprimidos) | Pesan demasiado para GitHub | Preparar datos y reentrenar (rutas B y C) | Paso B4 |
| Dataset del conjunto final, JMuBEN (unos 1.3 GB) | Pesa demasiado para GitHub | Repetir la evaluación final | Paso B5 |
| Entorno de Python (`ml\.venv`) | Es propio de cada equipo | Cualquier script de Python (ruta B) | Pasos B1 y B2 |
| Dependencias de la página web (`node_modules`) | Se regeneran | Modificar la página de descarga | Sección "La página de descarga" |
| Almacén de claves de la firma (`android\cafe-detector-release.jks` y `android\keystore.properties`) | Son secretos; no se suben a git | Generar un APK de distribución firmado con la misma firma | Pídeselos al dueño del proyecto, o crea los tuyos (paso A8) |
| `android\local.properties` | Contiene la ruta del SDK de tu equipo | Compilar la app | Android Studio lo crea solo |

### Qué SÍ viene y no tienes que generar

- El modelo ya entrenado, dentro de la app (`android\app\src\main\assets\model.tflite`).
- El modelo en formato Keras (`ml\outputs\final\model.keras`), para repetir la conversión sin reentrenar.
- Las imágenes de referencia de las pruebas (`golden`).
- Todos los resultados (`ml\outputs\`) y la documentación (`docs\`).
- El APK ya firmado, dentro de la página de descarga (`docs\landing-detector-hojas-cafe\public\BioCafe-v3.0.apk`).

**Para abrir, compilar y modificar la app basta con clonar el repositorio y seguir la ruta A.** No hace falta ningún dataset.

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

Resultado esperado: `BUILD SUCCESSFUL`, 16 pruebas unitarias sin fallos y el APK en `app\build\outputs\apk\debug\app-debug.apk`.

Con el emulador encendido:

```powershell
.\gradlew.bat connectedDebugAndroidTest
```

Resultado esperado: 10 pruebas instrumentadas sin fallos (una de ellas se omite si no hay fotos de lote).

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

### A8. Generar un APK firmado (opcional)

La compilación de depuración (`assembleDebug`) funciona sin nada más y sirve para probar. Para un APK de distribución (`assembleRelease`) hace falta un almacén de claves; sin él, el APK sale **sin firmar** y Android no lo instala.

**Si tienes el almacén original:** copia `cafe-detector-release.jks` y `keystore.properties` a la carpeta `android\`.

**Si no lo tienes, crea uno propio** (desde la carpeta `android`; `keytool` viene con el JDK de Android Studio):

```powershell
& "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe" -genkeypair -keystore mi-firma.jks -alias cafedetector -keyalg RSA -keysize 2048 -validity 10000
```

Te pedirá una contraseña y unos datos. Después crea el archivo `android\keystore.properties` con este contenido:

```
storeFile=mi-firma.jks
storePassword=TU_CONTRASEÑA
keyAlias=cafedetector
keyPassword=TU_CONTRASEÑA
```

Y compila:

```powershell
.\gradlew.bat assembleRelease
```

El APK queda en `app\build\outputs\apk\release\app-release.apk`.

Importante: un APK firmado con **otra** firma no se instala encima de la versión original; hay que desinstalar primero la app del teléfono. Guarda tu almacén y su contraseña fuera de git.

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
.\.venv\Scripts\python.exe 03_evaluar.py --run final             # make eval
.\.venv\Scripts\python.exe 04_convertir_tflite.py --run final    # make tflite
.\.venv\Scripts\python.exe 05_paridad_tflite.py --run final      # make parity
.\.venv\Scripts\python.exe generar_resultados.py     # make results
```

Qué necesita cada uno:

| Script | Necesita |
|---|---|
| `01_preparar_datos.py` | Los datasets descargados (paso B4) |
| `03`, `04`, `05` | `ml\outputs\final\model.keras` y los datos preparados |
| `generar_resultados.py` | Solo los archivos de `ml\outputs\` (ya vienen en el proyecto) |

### B4. Descargar los datasets de entrenamiento (solo si vas a preparar datos)

Ocupan unos 900 MB comprimidos y unos 3 GB descomprimidos. Los tres tienen licencia CC BY 4.0.

| Dataset | Enlace | Archivos que hay que bajar |
|---|---|---|
| RoCoLe | https://data.mendeley.com/datasets/c5yvn32dzg/2 | `RoCoLe-voc.tar.gz` y `RoCoLE-json.json` |
| DECAFIA | https://zenodo.org/records/19931904 | `CoffeeLeaf-CO.zip` |
| BRACOL | https://data.mendeley.com/datasets/yy2k5y8mxg/1 | `BRACOL_coffee_leaf_ images_datasets.zip` |

Desde la raíz del proyecto, crea las carpetas, copia en ellas los archivos descargados y descomprime:

```powershell
mkdir ml\data\raw\rocole, ml\data\raw\decafia, ml\data\external\bracol\x
# copia RoCoLe-voc.tar.gz y RoCoLE-json.json a ml\data\raw\rocole
# copia CoffeeLeaf-CO.zip a ml\data\raw\decafia
# copia el zip de BRACOL a ml\data\external\bracol y renómbralo a bracol.zip
tar -xzf ml\data\raw\rocole\RoCoLe-voc.tar.gz -C ml\data\raw\rocole
Expand-Archive ml\data\raw\decafia\CoffeeLeaf-CO.zip -DestinationPath ml\data\raw\decafia
tar -xf ml\data\external\bracol\bracol.zip -C ml\data\external\bracol\x
```

**Sobre BRACOL:** el archivo publicado está incompleto de origen. El Explorador de Windows y `Expand-Archive` lo rechazan; por eso se usa `tar`, que extrae lo que hay. Es normal que termine con un error de descompresión en el último archivo: se recuperan 1402 imágenes de 1747 y el script ya cuenta con ello.

Debe quedar esta estructura:

```
ml\data\raw\rocole\RoCoLE-json.json
ml\data\raw\rocole\export\*.jpeg
ml\data\raw\decafia\CoffeeLeaf-CO\images\...
ml\data\raw\decafia\CoffeeLeaf-CO\labels\...
ml\data\external\bracol\x\coffee-datasets\coffee-datasets\leaf\dataset.csv
ml\data\external\bracol\x\coffee-datasets\coffee-datasets\leaf\images\*.jpg
```

Después ejecuta `01_preparar_datos.py` (paso B3). Resultado esperado: 3736 imágenes y la línea de comprobación de fugas con los tres contadores en 0. Si el número difiere, revisa que los tres datasets estén completos.

### B5. Descargar el conjunto final, JMuBEN (solo para repetir la evaluación final)

Son unos 1.3 GB. No se usa para entrenar; sirve únicamente para `evaluar_conjunto_final.py`.

| Página | Archivos que hay que bajar |
|---|---|
| https://data.mendeley.com/datasets/t2r6rszp5c/1 | El zip de `Leaf rust` |
| https://data.mendeley.com/datasets/tgv3zb82nd/1 | Los zip de `Healthy` y `Miner` |

Copia los tres zip, sin descomprimir, a `ml\data\final_holdout\jmuben\`. El script los descomprime solo:

```powershell
cd ml
.\.venv\Scripts\python.exe evaluar_conjunto_final.py --run final
```

Este conjunto ya se evaluó una vez con el modelo actual (resultado en `docs\resultados.md`). Si lo usas para tomar decisiones sobre un modelo nuevo, deja de ser un conjunto final independiente.

---

## Ruta C. Volver a entrenar en Google Colab

Solo si cambias los datos o el entrenamiento. Necesitas una cuenta de Google.

> El entrenamiento se lanzó desde Linux con la CLI de Colab, que **no funciona en Windows**. En Windows hay que hacerlo desde el navegador. **Este camino no se ha probado.** El cuaderno `ml/colab_entrenamiento.ipynb` corresponde al modelo v1 y está desactualizado; usa los pasos de abajo.

### C1. Preparar los dos paquetes

Con el entorno de la ruta B y los datos ya preparados (`01_preparar_datos.py`, que además necesita BRACOL en `ml\data\external\bracol`):

```powershell
cd ml
.\.venv\Scripts\python.exe crear_bundle.py          # cafe_ml_bundle.zip (código)
.\.venv\Scripts\python.exe crear_bundle.py --data   # cafe_data_v2.zip (datos, unos 175 MB)
cd ..
```

### C2. Ejecutar en Colab

1. Abre https://colab.research.google.com/ y crea un cuaderno nuevo.
2. `Entorno de ejecución` → `Cambiar tipo de entorno de ejecución` → **GPU T4**.
3. Sube los dos zip con el panel de archivos (icono de carpeta) a `/content/`.
4. En una celda, ejecuta:

```
!cd /content && unzip -q -o cafe_ml_bundle.zip && unzip -q -o cafe_data_v2.zip
!cd /content/ml && python colab_run_v3.py
```

5. Cuando imprima `ALL DONE`, descarga `/content/cafe_outputs_v3.zip`.

El script hace dos entrenamientos de EfficientNet-B0 con las cuatro clases: uno sin BRACOL, para medir en una fuente no vista, y el modelo final con todas las fuentes. Duración de referencia en una T4: unos 50 minutos en total.

### C3. Llevar el modelo nuevo a la app

Descomprime `cafe_outputs_v3.zip`, copia su carpeta `outputs\final` a `ml\outputs\final` y, desde la raíz del proyecto:

```powershell
cd ml
.\.venv\Scripts\python.exe 04_convertir_tflite.py --run final
.\.venv\Scripts\python.exe 05_paridad_tflite.py --run final
cd ..
Copy-Item ml\outputs\final\model_fp32.tflite android\app\src\main\assets\model.tflite
Copy-Item ml\outputs\final\labels.txt, ml\outputs\final\threshold.json android\app\src\main\assets\
Copy-Item ml\outputs\final\golden\* android\app\src\androidTest\assets\golden\
ml\.venv\Scripts\python.exe ml\generar_resultados.py
```

La app usa el modelo **sin cuantizar** (`model_fp32.tflite`).

**Cuidado con `threshold.json`:** el del proyecto se escribió a mano, con el umbral 0.60 y la regla de duda entre arañita roja y roya (`"doubt": {"classes": ["arana_roja", "roya"], "margin": 0.4}`). Al reentrenar, `03_evaluar.py` lo sobrescribe con otro umbral y sin esa regla. Antes de copiarlo a la app, vuelve a poner los valores que correspondan; el motivo de cada uno está en `docs/decisiones.md` y en `ml\outputs\final\threshold_source.json`.

Después repite el paso A6: las pruebas deben seguir en verde con el modelo nuevo.

---

## La página de descarga

Está en `docs\landing-detector-hojas-cafe` (Next.js). Solo hace falta si vas a modificarla.

1. Instala Node.js (https://nodejs.org/, versión LTS) y después pnpm: `npm install -g pnpm`.
2. Desde esa carpeta:

```powershell
pnpm install
pnpm dev      # la abre en http://localhost:3000
pnpm build    # comprueba que compila antes de publicar
```

Para publicarla en Vercel, importa el repositorio y pon como "Root Directory" `docs/landing-detector-hojas-cafe`.

Si generas un APK nuevo, reemplaza `public\BioCafe-v3.0.apk` y actualiza la versión y el tamaño en `components\landing\hero.tsx`.

---

## Lista de comprobación

- [ ] Android Studio abre la carpeta `android` y la sincronización de Gradle termina sin errores.
- [ ] `.\gradlew.bat testDebugUnitTest assembleDebug` termina con `BUILD SUCCESSFUL`.
- [ ] La app abre en el emulador y muestra "BioCafe".
- [ ] "Elegir de galería" con una foto de hoja lleva a la pantalla de resultado.
- [ ] `.\gradlew.bat connectedDebugAndroidTest` pasa las 10 pruebas con el emulador encendido.

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `SDK location not found` | Falta `android\local.properties` | Abre el proyecto con Android Studio, que lo crea |
| Error de sincronización que menciona `compileSdk 37` o una plataforma no encontrada | Falta la plataforma API 37 | Paso A2 |
| Error de versión de Java al sincronizar | JDK no compatible | Instala Temurin 21 y selecciónalo (paso A3) |
| `assembleRelease` genera un APK que el teléfono no instala | Falta el almacén de claves y el APK salió sin firmar | Paso A8 |
| `01_preparar_datos.py` da menos de 3736 imágenes o falla al leer BRACOL | Falta un dataset o BRACOL no se extrajo con `tar` | Paso B4 |
| `No matching distribution found for tensorflow==2.21.0` | Python 3.14 u otra versión no admitida | Usa `--python 3.12` (paso B2) |
| El emulador clasifica una sala como "Hoja sana" | La cámara del emulador no muestra una hoja y el modelo solo conoce hojas | Es una limitación conocida; prueba con fotos desde la galería |

## Para saber más

- `README.md`: resumen y reproducción en Linux.
- `docs/resultados.md`: métricas y limitaciones del modelo.
- `docs/bitacora.md` y `docs/decisiones.md`: qué se hizo en cada fase y por qué.
