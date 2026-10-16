# Glosario

Términos técnicos que aparecen en el tutorial, en orden alfabético. Cada entrada indica dónde aparece por primera vez o dónde se explica mejor. Volver al [índice](index.md).

---

**Ajuste fino (*fine-tuning*)**
Segunda etapa del entrenamiento: se descongela la red base y se entrena todo el modelo con una tasa de aprendizaje pequeña, para adaptarlo sin borrar lo que ya sabía.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**API**
Interfaz de programación: el conjunto de clases y funciones que una librería ofrece para que otro programa la use. En BioCafe, la API de LiteRT es la clase `Interpreter`.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md).

**APK**
Archivo con el que se instala una app en Android. Contiene el código compilado, los recursos y, en BioCafe, el modelo en la carpeta de *assets*.
Dónde aparece: [Capítulo 10](10_orquestacion_y_entrega.md).

**Assets**
Carpeta de una app Android (`src/main/assets/`) cuyos archivos viajan tal cual dentro del APK. Aquí están `model.tflite`, `labels.txt`, `threshold.json` y `conditions.json`.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md).

**Aumento de datos (*data augmentation*)**
Técnica que genera variaciones de cada foto de entrenamiento (giros, espejos, zoom, brillo) para que el modelo aprenda a reconocer la hoja aunque cambie la toma.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Batch (lote)**
Grupo de imágenes que el modelo procesa juntas en un paso del entrenamiento. En BioCafe el tamaño de lote es 32 (`BATCH_SIZE`).
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**BatchNormalization**
Capa de una red neuronal que normaliza sus valores internos con estadísticas aprendidas. En el ajuste fino de BioCafe se deja congelada.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Calibración**
Qué tan bien coincide la confianza que declara el modelo con lo que realmente acierta. Se mide con el error de calibración esperado (ECE).
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**CameraX**
Librería de Android que simplifica el uso de la cámara: vista previa, captura y manejo automático del ciclo de vida.
Dónde aparece: [Capítulo 9](09_las_pantallas.md).

**CNN (red neuronal convolucional)**
Tipo de red neuronal especializada en imágenes: aprende filtros que detectan bordes, texturas y formas. EfficientNet-B0 y MobileNetV2 son CNN.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Colab (Google Colab)**
Servicio de Google para ejecutar cuadernos y scripts de Python en la nube, con acceso a GPU. Allí se entrena el modelo entregado.
Dónde aparece: [Capítulo 3](03_entrenamiento.md), [Capítulo 10](10_orquestacion_y_entrega.md).

**Compose (Jetpack Compose)**
Forma moderna de construir interfaces en Android escribiendo funciones Kotlin marcadas con `@Composable` que describen la pantalla según el estado.
Dónde aparece: [Capítulo 9](09_las_pantallas.md).

**Contrato del modelo**
Conjunto de reglas compartidas entre Python y la app: entrada, normalización, redimensionado, salida y orden de clases.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md).

**Corrutina**
Mecanismo de Kotlin para ejecutar trabajo en segundo plano (por ejemplo, cargar el modelo) sin congelar la pantalla y sin manejar hilos a mano.
Dónde aparece: [Capítulo 8](08_estado_y_navegacion.md).

**Cuantización de rango dinámico**
Conversión que guarda los pesos del modelo con 8 bits en lugar de 32, para que el archivo sea más pequeño. BioCafe la genera pero no la usa en la app.
Dónde aparece: [Capítulo 5](05_conversion_y_paridad.md).

**CUDA**
Plataforma de NVIDIA que permite a TensorFlow usar la GPU. El Makefile ajusta la ruta de sus librerías.
Dónde aparece: [Capítulo 10](10_orquestacion_y_entrega.md).

**Dataset**
Colección de datos organizada para entrenar o evaluar un modelo; aquí, fotos de hojas con su etiqueta. BioCafe usa RoCoLe, DECAFIA, BRACOL y JMuBEN.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md).

**dHash (hash de diferencias)**
Huella perceptual de una imagen: se reduce a pocos píxeles en gris y se anota si cada píxel es más claro que su vecino. Dos fotos parecidas dan huellas parecidas.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md).

**Dropout**
Capa que, durante el entrenamiento, apaga al azar una parte de los valores para que el modelo no memorice.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**EfficientNet-B0**
Red convolucional compacta, preentrenada con ImageNet, que BioCafe usa como base. Se eligió frente a MobileNetV2 por su mejor resultado en una fuente no vista.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Época**
Una pasada completa del modelo por todas las imágenes de entrenamiento.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Estrato**
Subgrupo de los datos definido por una combinación de rasgos; en BioCafe, la pareja (fuente, clase), por ejemplo `rocole/roya`.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md), [Capítulo 3](03_entrenamiento.md).

**Exactitud (*accuracy*)**
Fracción de imágenes que el modelo clasifica correctamente.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**EXIF**
Metadatos guardados dentro de una foto JPEG; uno de ellos indica cómo girarla para verla derecha.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md).

**F1 y F1 macro**
F1 combina precisión y recall de una clase en un solo número. El F1 macro es el promedio simple del F1 de las clases, así que una clase pequeña pesa igual que una grande.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**fp32 (*float32*)**
Número decimal de 32 bits. "Modelo fp32" significa que sus pesos se guardan sin cuantizar; es el que lleva la app.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md), [Capítulo 5](05_conversion_y_paridad.md).

**Golden (imágenes de referencia)**
Diez imágenes de prueba exportadas con las probabilidades exactas que la app debe reproducir.
Dónde aparece: [Capítulo 5](05_conversion_y_paridad.md).

**GPU**
Procesador gráfico; hace en paralelo los cálculos de una red neuronal y acelera mucho el entrenamiento.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Gradle**
Herramienta que compila un proyecto Android, descarga sus dependencias y genera el APK.
Dónde aparece: [Capítulo 10](10_orquestacion_y_entrega.md).

**Holdout (conjunto apartado)**
Datos que se separan y no se usan para entrenar. BioCafe usa BRACOL como fuente apartada para elegir arquitectura y umbral, y JMuBEN como conjunto final.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**ImageNet**
Gran colección pública de fotos de objetos cotidianos con la que se preentrenan muchas redes, entre ellas EfficientNet-B0.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Inferencia**
Usar un modelo ya entrenado para obtener una predicción sobre una entrada nueva.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md).

**Interpreter**
Clase de LiteRT (`org.tensorflow.lite.Interpreter`) que carga un modelo TFLite y lo ejecuta.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md).

**JMuBEN**
Dataset público de hojas de café arábica de Kenia, usado solo como conjunto final de evaluación.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**Keras**
Librería de Python, integrada con TensorFlow, para construir y entrenar redes neuronales. El modelo entrenado se guarda como `model.keras`.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Kotlin**
Lenguaje de programación con que está escrita la app Android.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md), [Capítulo 6](06_clasificador_en_el_telefono.md).

**kotlinx.serialization**
Librería de Kotlin que convierte JSON en objetos (por ejemplo, `threshold.json` en `ThresholdConfig`).
Dónde aparece: [Capítulo 7](07_logica_de_decision.md).

**Label smoothing**
Técnica que suaviza las etiquetas de entrenamiento para que el modelo no aprenda a estar 100 % seguro.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**LiteRT**
Nombre actual de TensorFlow Lite para dispositivos: la librería que ejecuta el modelo en el teléfono.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md).

**Makefile**
Archivo que define atajos de comandos (`make data`, `make tflite`...) para ejecutar los pasos del pipeline en orden.
Dónde aparece: [Capítulo 10](10_orquestacion_y_entrega.md).

**Matriz de confusión**
Tabla que cruza la clase real (filas) con la clase predicha (columnas); muestra qué clases se confunden entre sí.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**MD5**
Función que resume un archivo en una huella corta; dos archivos idénticos byte a byte tienen la misma huella.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md).

**MobileNetV2**
Red convolucional ligera, base del plan original y de la versión 1 del modelo; fue reemplazada por EfficientNet-B0.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**MVVM (Modelo–Vista–ViewModel)**
Patrón de arquitectura que separa los datos y la lógica (ViewModel) de lo que se dibuja (Vista).
Dónde aparece: [Capítulo 8](08_estado_y_navegacion.md).

**NavHost**
Componente de Compose que decide qué pantalla mostrar según la ruta actual (inicio, cámara o resultado).
Dónde aparece: [Capítulo 8](08_estado_y_navegacion.md).

**Next.js**
Framework web basado en React con el que está hecha la página de descarga del APK.
Dónde aparece: [Capítulo 10](10_orquestacion_y_entrega.md).

**Normalización**
Transformar los valores de los píxeles a la escala que espera la red. En BioCafe ocurre dentro del modelo, nunca en la app.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md).

**Parada temprana (*early stopping*)**
Detener el entrenamiento cuando la pérdida de validación deja de mejorar, y recuperar los mejores pesos.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Paridad**
Comprobación de que dos versiones del mismo modelo (Keras y TFLite, o Python y Android) dan las mismas respuestas. BioCafe la prueba en dos niveles.
Dónde aparece: [Capítulo 5](05_conversion_y_paridad.md).

**Pérdida (*loss*)**
Número que mide cuánto se equivoca el modelo durante el entrenamiento; entrenar es intentar bajarlo.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Permiso (Android)**
Autorización que una app declara en su manifiesto y que el usuario concede. BioCafe solo pide la cámara y no tiene permiso de internet.
Dónde aparece: [Capítulo 6](06_clasificador_en_el_telefono.md), [Capítulo 9](09_las_pantallas.md).

**Precisión (*precision*)**
De todas las veces que el modelo dijo "clase X", la fracción en que acertó.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**Python**
Lenguaje de programación del pipeline de aprendizaje automático (`ml/`).
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md).

**Recall (sensibilidad)**
De todas las imágenes que realmente son de la clase X, la fracción que el modelo reconoció.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**Regla de duda**
Regla de BioCafe: si las dos clases más probables son arañita roja y roya y su diferencia es menor que 0.4, la app muestra ambas en lugar de elegir una.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md), [Capítulo 7](07_logica_de_decision.md).

**Semilla (*seed*)**
Número que fija los resultados "aleatorios" para que un proceso se pueda repetir igual. En BioCafe es 42.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md).

**Softmax**
Función que convierte las salidas de la red en probabilidades positivas que suman 1.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md), [Capítulo 3](03_entrenamiento.md).

**Split (partición)**
División de los datos en entrenamiento, validación y prueba. En BioCafe es 70/15/15 por grupos.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md).

**Squash**
Redimensionar la foto completa a 224×224 sin recortar ni conservar la proporción.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md).

**StateFlow**
Tipo de Kotlin que guarda un valor observable; las pantallas se redibujan cuando cambia. El ViewModel publica su estado con él.
Dónde aparece: [Capítulo 8](08_estado_y_navegacion.md).

**Tasa de aprendizaje (*learning rate*)**
Tamaño de los pasos con que el entrenamiento corrige los pesos del modelo. BioCafe usa `1e-3` para la cabeza y `1e-4` para el ajuste fino.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Tensor**
Arreglo de números con varias dimensiones. La entrada del modelo es un tensor de forma `[1, 224, 224, 3]`.
Dónde aparece: [Capítulo 1](01_contrato_del_modelo.md).

**TensorFlow**
Librería de Google para aprendizaje automático con la que se entrena, evalúa y convierte el modelo.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Test (conjunto de prueba)**
Parte de los datos que no se usa para entrenar ni para decidir, y sirve para calificar el modelo.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md), [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**TFLite (TensorFlow Lite)**
Formato compacto de modelo para teléfonos y dispositivos pequeños. El archivo de la app es `model.tflite`.
Dónde aparece: [Capítulo 5](05_conversion_y_paridad.md).

**Transfer learning (aprendizaje por transferencia)**
Reutilizar una red ya entrenada en otra tarea y adaptarla a la nueva con pocos datos.
Dónde aparece: [Capítulo 3](03_entrenamiento.md).

**Umbral de confianza**
Probabilidad mínima para que la app afirme una clase. En BioCafe es 0.60; por debajo, la app dice que no pudo determinar.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md), [Capítulo 7](07_logica_de_decision.md).

**Union-find**
Estructura de datos que agrupa elementos conectados. BioCafe la usa para reunir copias de una misma foto.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md).

**Validación (conjunto de validación)**
Parte de los datos que se usa durante el entrenamiento para decidir cuándo parar, sin entrenar con ella.
Dónde aparece: [Capítulo 2](02_preparacion_de_datos.md), [Capítulo 3](03_entrenamiento.md).

**Validación cruzada**
Dividir los datos en K pliegues y entrenar K veces, probando cada vez con un pliegue distinto, para que cada imagen se pruebe una vez.
Dónde aparece: [Capítulo 4](04_evaluacion_umbral_y_duda.md).

**ViewModel**
Clase de Android que guarda el estado de la interfaz y sobrevive a la rotación de la pantalla. En BioCafe es `ClassifierViewModel`.
Dónde aparece: [Capítulo 8](08_estado_y_navegacion.md).
