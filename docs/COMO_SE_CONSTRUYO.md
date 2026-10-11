# Cómo se construyó BioCafe

Una explicación paso a paso, pensada para alguien que no sabe de inteligencia artificial ni de apps. Cada parte dice qué es, con qué lenguaje se hizo y para qué sirve.

## La idea en una frase

BioCafe es una app de teléfono que mira la foto de una hoja de café y dice si está sana o si tiene roya, minador o arañita roja. Lo hace sola, dentro del teléfono, sin internet.

## Cómo pensarlo

Imagina que quieres enseñarle a un niño a reconocer hojas enfermas:

1. Le muestras **muchas fotos** y le dices qué tiene cada una.
2. El niño **practica** hasta que acierta casi siempre.
3. Le haces un **examen** con fotos que nunca vio.
4. Si aprueba, lo **llevas al campo** para que ayude.

BioCafe se hizo igual. El "niño" es un programa llamado **modelo**, y el "campo" es tu teléfono.

## El recorrido completo

```
 FOTOS de hojas          PREPARAR             ENSEÑAR            EXAMINAR
 (de internet)    --->   ordenar y     --->   al modelo   --->   con fotos
 3736 imágenes           quitar copias        (en Colab)         nuevas
                                                                    |
                                                                    v
 PÁGINA WEB       <---   APP ANDROID   <---   EMPAQUETAR  <---   ¿aprobó?
 para descargar          (BioCafe)            el modelo
                                              para teléfono
```

Hay dos mundos que se hicieron por separado y luego se juntaron:

| Mundo | Qué se hace ahí | Dónde corre |
|---|---|---|
| **La escuela** | Enseñar y examinar al modelo | En un computador y en la nube |
| **El teléfono** | Usar el modelo ya enseñado | En tu bolsillo |

## Las piezas y sus lenguajes

Un "lenguaje de programación" es el idioma en que se le escriben instrucciones al computador. BioCafe usa varios, cada uno para lo que mejor sabe hacer.

| Pieza | Lenguaje | Herramientas | Para qué sirve | Dónde está |
|---|---|---|---|---|
| Preparar las fotos | **Python** | Pillow, NumPy | Ordenar las fotos, quitar las repetidas y repartirlas | `ml/01_preparar_datos.py` |
| Enseñar al modelo | **Python** | TensorFlow, Keras | Que el modelo aprenda viendo fotos | `ml/02_entrenar.py` |
| Examinar al modelo | **Python** | scikit-learn, Matplotlib | Contar aciertos y errores | `ml/03_evaluar.py` |
| Empaquetar el modelo | **Python** | TensorFlow Lite | Convertirlo a un archivo que entiende el teléfono | `ml/04_convertir_tflite.py` |
| La app | **Kotlin** | Android Studio, Jetpack Compose | Las pantallas, la cámara y usar el modelo | `android/` |
| Los textos y fichas | **JSON** y **XML** | — | Guardar nombres, síntomas y textos de las pantallas | `android/app/src/main/assets/` y `res/` |
| Armar la app | **Kotlin (Gradle)** | Gradle | Juntar todo en un archivo instalable | `android/app/build.gradle.kts` |
| La página de descarga | **TypeScript** | Next.js, React, Tailwind | La página web con el botón de descarga | `docs/landing-detector-hojas-cafe/` |
| Los atajos | **Make** | — | Lanzar cada paso con una palabra corta | `Makefile` |
| Guardar el historial | — | Git y GitHub | Recordar cada cambio y tener copia en la nube | todo el repositorio |

## Paso a paso

### Paso 1. Reunir las fotos

**En palabras simples:** para enseñar, primero hacen falta ejemplos.

Las fotos salieron de colecciones públicas de internet hechas por investigadores, todas con permiso de uso (licencia CC BY 4.0):

| Colección | De dónde es | Qué aportó |
|---|---|---|
| RoCoLe | Ecuador | Hojas sanas, con roya y con arañita roja |
| DECAFIA | Colombia (Santander) | Hojas sanas, con roya y con minador |
| BRACOL | Brasil | Hojas sanas, con roya y con minador |

Cada foto viene con una **etiqueta**: una nota que dice qué tiene la hoja. Sin etiquetas no se puede enseñar.

### Paso 2. Preparar las fotos

**En palabras simples:** antes de estudiar hay que ordenar los apuntes y tirar los repetidos.

Lo hace `ml/01_preparar_datos.py`, escrito en **Python**. Hace cuatro cosas:

1. **Traduce las etiquetas** de cada colección a las cuatro clases de BioCafe.
2. **Quita las fotos repetidas.** Encontró más de 500 copias, algunas giradas o reflejadas. Para detectarlas calcula una "huella" de cada imagen y compara huellas.
3. **Reparte las fotos en tres montones:**

   | Montón | Parte | Para qué |
   |---|---|---|
   | Entrenamiento | 70 % | Las que el modelo estudia |
   | Validación | 15 % | Para saber cuándo dejar de estudiar |
   | Prueba | 15 % | El examen final; nunca las ve mientras estudia |

4. **Comprueba que no haya trampa:** ninguna foto puede estar en dos montones, y las fotos de una misma planta van siempre juntas. Si el modelo viera en el examen una foto que ya estudió, la nota sería falsa.

Resultado: 3736 fotos listas.

### Paso 3. Enseñar al modelo

**En palabras simples:** el modelo mira una foto, adivina, le dicen si acertó y se corrige un poquito. Repite eso miles de veces.

Lo hace `ml/02_entrenar.py`, en **Python** con **TensorFlow** y **Keras**, que son herramientas hechas para esto.

- **No se empieza de cero.** Se parte de un modelo llamado **EfficientNet-B0**, que ya aprendió a ver formas, colores y bordes con millones de fotos de todo tipo. Solo hay que enseñarle lo nuevo: hojas de café. Es como contratar a alguien que ya sabe leer y enseñarle un tema, en vez de enseñarle el abecedario.
- **Se le muestran las fotos cambiadas a propósito:** giradas, más claras, más oscuras, más cerca. Así aprende la enfermedad y no la foto de memoria.
- **Se entrena en la nube**, en **Google Colab**, que presta un computador con una tarjeta gráfica potente (GPU). Con ella el entrenamiento tarda unos 25 minutos; sin ella, horas.

Al terminar queda un archivo, `model.keras`: es el "cerebro" ya enseñado.

### Paso 4. Examinar al modelo

**En palabras simples:** se le pone un examen con fotos que nunca vio y se cuentan los aciertos.

Lo hace `ml/03_evaluar.py`. Se hicieron dos exámenes:

| Examen | Con qué fotos | Resultado |
|---|---|---|
| Interno | Del montón de prueba, mismas colecciones | 94 de cada 100 |
| Externo | De JMuBEN, una colección de Kenia que nunca se usó para enseñar | 81 de cada 100 |

El segundo es el que importa: dice cómo le va con hojas realmente nuevas. Que sea más bajo es normal y hay que decirlo.

También se elige aquí el **umbral de confianza**: qué tan seguro tiene que estar el modelo para que la app muestre una respuesta. Si no llega, la app dice "No se pudo determinar con seguridad".

### Paso 5. Empaquetar el modelo para el teléfono

**En palabras simples:** el cerebro está en un formato de computador grande; hay que pasarlo a uno que el teléfono entienda.

Lo hace `ml/04_convertir_tflite.py`. Convierte `model.keras` en `model.tflite`, un archivo de 16 MB en formato **TensorFlow Lite**, pensado para teléfonos.

### Paso 6. Comprobar que no se dañó al empaquetar

**En palabras simples:** si copias un dibujo, hay que comprobar que la copia quedó igual.

Lo hace `ml/05_paridad_tflite.py`. Pasa las mismas fotos por el modelo original y por el empaquetado, y compara. También guarda 10 fotos con sus respuestas esperadas, llamadas **vectores de referencia**: más adelante la app tiene que dar esas mismas respuestas.

### Paso 7. Construir la app

**En palabras simples:** ya hay cerebro; ahora hay que hacerle cuerpo: ojos (cámara), boca (pantallas) y manos (botones).

La app está escrita en **Kotlin**, el lenguaje oficial para Android. Sus partes:

| Parte | Archivo | Qué hace |
|---|---|---|
| Pantallas | `ui/HomeScreen.kt`, `CameraScreen.kt`, `ResultScreen.kt` | Lo que ves y tocas. Hechas con **Jetpack Compose** |
| Cámara | `ui/CameraScreen.kt` | Toma la foto. Usa **CameraX** |
| Preparar la imagen | `ml/ImageUtils.kt` | Endereza la foto y la reduce |
| El que pregunta al modelo | `ml/CoffeeLeafClassifier.kt` | Le pasa la foto al modelo y recibe la respuesta. Usa **LiteRT** |
| Las reglas | `ml/ClassifierLogic.kt` | Decide qué mostrar: resultado, duda o "no se pudo" |
| Las fichas | `data/ConditionsRepository.kt` | Lee los síntomas de cada enfermedad |
| El director | `ui/ClassifierViewModel.kt` | Coordina todo y recuerda el resultado si giras el teléfono |

### Paso 8. Probar todo

**En palabras simples:** antes de entregar algo, se revisa que funcione.

| Tipo de prueba | Cuántas | Dónde corren | Qué revisan |
|---|---|---|---|
| Unitarias | 16 | En el computador | Las reglas: orden de las respuestas, umbral, duda |
| Instrumentadas | 10 | En un teléfono o emulador | Que el modelo dé en el teléfono lo mismo que en el computador, y cuánto tarda |

En un teléfono real (Motorola Edge 30) el modelo responde en unos 48 milisegundos: más rápido que un parpadeo.

### Paso 9. Armar el archivo instalable

**En palabras simples:** se mete todo en una caja y se le pone un sello para que se sepa quién la hizo.

**Gradle** junta el código, el modelo, los textos y el ícono en un solo archivo, el **APK**. Después se **firma** con una clave secreta: Android solo deja instalar una actualización si trae la misma firma que la versión anterior.

### Paso 10. La página para descargarla

**En palabras simples:** una vitrina con un botón que dice "Descargar".

Está hecha en **TypeScript** con **Next.js**. El diseño inicial lo generó la herramienta v0 y luego se refinó para que se pareciera a la app. Se publica en **Vercel**, un servicio que pone páginas en internet.

### Paso 11. Guardar todo

**En palabras simples:** un cuaderno que recuerda cada cambio, con copia en una caja fuerte.

**Git** guarda el historial: qué se cambió, cuándo y por qué. **GitHub** guarda una copia en internet. Las fotos y la clave de la firma no se suben: las fotos pesan demasiado y la clave es secreta.

## Qué pasa cuando tomas una foto

Todo esto ocurre dentro del teléfono, en menos de un segundo:

```
1. Tomas la foto o la eliges de la galería
        |
2. La app la endereza y la reduce a 224 x 224 puntos
        |
3. Convierte cada punto en tres números: cuánto rojo, verde y azul tiene
        |
4. Le pasa esos números al modelo
        |
5. El modelo devuelve cuatro números: qué tan probable es cada clase
   ejemplo:  roya 87 %, arañita roja 9 %, sana 3 %, minador 1 %
        |
6. Las reglas deciden qué mostrar
        |
7. Aparece el resultado con su ficha de síntomas
```

Las reglas del paso 6, en orden:

| Si pasa esto… | La app muestra… |
|---|---|
| Arañita roja y roya quedan muy parejas | "Puede ser … o …", con las dos fichas |
| Ninguna clase llega al 60 % | "No se pudo determinar con seguridad" |
| Una clase gana con claridad | El resultado y su ficha |

La foto nunca sale del teléfono: la app ni siquiera tiene permiso de internet.

## Los archivos que unen los dos mundos

La escuela y el teléfono se hicieron por separado. Cuatro archivos pasan de un lado al otro, y los dos lados deben estar de acuerdo sobre ellos:

| Archivo | Qué contiene | Quién lo crea |
|---|---|---|
| `model.tflite` | El cerebro ya enseñado | El paso 5 |
| `labels.txt` | Los nombres de las cuatro clases, en orden | El paso 3 |
| `threshold.json` | El umbral de confianza y la regla de duda | El paso 4 |
| `conditions.json` | El nombre y los síntomas de cada clase | Escrito a mano, con texto del informe |

Viven en `android/app/src/main/assets/`.

Hay un acuerdo, llamado **contrato**, que ambos lados respetan: la imagen entra siempre como 224 × 224 puntos, con colores de 0 a 255, y el modelo responde con una probabilidad por clase en el orden de `labels.txt`. Si un lado lo cambiara sin avisar al otro, la app respondería disparates.

## Glosario

| Palabra | Qué significa |
|---|---|
| Modelo | El programa que aprendió a reconocer hojas |
| Entrenar | Enseñarle al modelo mostrándole ejemplos |
| Etiqueta | La nota que dice qué tiene cada foto |
| Clase | Cada respuesta posible: sana, roya, minador, arañita roja |
| Dataset | Una colección de fotos con etiquetas |
| GPU | Tarjeta gráfica; hace los cálculos del entrenamiento mucho más rápido |
| Colab | Servicio de Google que presta computadores con GPU |
| TFLite / LiteRT | El formato y el motor que permiten usar el modelo en un teléfono |
| APK | El archivo con el que se instala una app Android |
| Umbral | La seguridad mínima que se le exige al modelo para mostrar una respuesta |
| Emulador | Un teléfono de mentira dentro del computador, para probar |
| Repositorio | La carpeta del proyecto con todo su historial |

## Lo que BioCafe no hace

- Solo conoce cuatro clases. Otras enfermedades las confundirá con alguna de ellas.
- Solo conoce hojas: si le muestras otra cosa, igual responde.
- La arañita roja es su clase más débil: solo hubo una colección para enseñársela.
- Confunde a veces el minador con la roya.
- No se ha probado con fotos tomadas en fincas de Colombia.
- Es un prototipo académico de apoyo, no una herramienta de diagnóstico.

## Para saber más

| Si quieres… | Lee |
|---|---|
| Instalarlo y modificarlo en Windows | `docs/MANUAL_WINDOWS.md` |
| Ver todas las cifras y sus límites | `docs/resultados.md` |
| Saber por qué se tomó cada decisión | `docs/decisiones.md` |
| Seguir la historia completa, paso a paso | `docs/bitacora.md` |
