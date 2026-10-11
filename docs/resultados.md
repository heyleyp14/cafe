# Resultados

Archivo generado por `ml/generar_resultados.py` a partir de `ml/outputs/`. No editar a mano.

Modelo `v3-2026-10`: efficientnetb0 con clases arana_roja, minador, roya, sana.

## Lo esencial

| Dónde se mide | Qué mide | Imágenes | Exactitud | F1 macro |
|---|---|---|---|---|
| Test interno | Imágenes de las mismas fuentes del entrenamiento | 556 | 0.9388 | 0.8611 |
| Conjunto final (JMuBEN) | Fuente nunca usada para entrenar ni para decidir | 44297 | **0.8125** | **0.7806** (3 clases presentes) |

La cifra que estima el comportamiento con imágenes nuevas es la del conjunto final, no la del test interno.

## Datos

| Fuente y clase | train | val | test |
|---|---|---|---|
| bracol / minador | 177 | 38 | 38 |
| bracol / roya | 326 | 70 | 69 |
| bracol / sana | 100 | 21 | 21 |
| decafia / minador | 261 | 56 | 55 |
| decafia / roya | 238 | 51 | 51 |
| decafia / sana | 499 | 106 | 106 |
| rocole / arana_roja | 108 | 22 | 22 |
| rocole / roya | 391 | 83 | 83 |
| rocole / sana | 522 | 111 | 111 |

Total: 3736 imágenes. Reparto estratificado por fuente y clase; desviación máxima respecto a 70/15/15: 0.0105. Duplicados eliminados: 538. Imágenes en dos particiones: 0 por MD5, 0 pares por hash perceptual y 0 grupos repartidos.

## Entrenamiento del modelo final

Hardware: Tesla T4. Tiempo: 1671.0 s. Épocas ejecutadas: 10 (cabeza) + 22 (ajuste fino). TensorFlow 2.21.0, Keras 3.15.1, Python 3.13.15. Pérdida de validación: 0.9312 en la época 1, mínimo 0.5126.

## Cómo se eligió la arquitectura (etapa 1)

Cada modelo de esta tabla se entrenó sin BRACOL y se midió en BRACOL, una fuente que no había visto. El F1 macro es sobre las tres clases que BRACOL contiene.

| Modelo | BRACOL exactitud | BRACOL F1 macro | Recall minador | Recall roya | Recall sana |
|---|---|---|---|---|---|
| v1 MobileNetV2 (3 clases) | 0.6872 | 0.626 | 0.4466 | 0.8925 | 0.4437 |
| v2 MobileNetV2 (3 clases) | 0.7767 | 0.7313 | 0.3676 | 0.9419 | 0.9648 |
| v2 EfficientNet-B0 (3 clases) | 0.8581 | 0.8494 | 0.6087 | 0.9613 | 0.9648 |
| v3 EfficientNet-B0 (4 clases) | 0.8663 | 0.8637 | 0.6245 | 0.9677 | 0.9648 |

BRACOL se usó para elegir la arquitectura y el umbral, y después se añadió al entrenamiento del modelo final; por eso sus cifras no son una estimación independiente.

## Test interno (556 imágenes)

Exactitud: 0.9388. F1 macro: 0.8611.

| Clase | Precisión | Recall | F1 | Imágenes |
|---|---|---|---|---|
| arana_roja | 0.5417 | 0.5909 | 0.5652 | 22 |
| minador | 0.9891 | 0.9785 | 0.9838 | 93 |
| roya | 0.9268 | 0.936 | 0.9314 | 203 |
| sana | 0.9702 | 0.958 | 0.9641 | 238 |

Filas: clase real. Columnas: predicción.

|  | arana_roja | minador | roya | sana |
|---|---|---|---|---|
| arana_roja | 13 | 0 | 6 | 3 |
| minador | 0 | 91 | 2 | 0 |
| roya | 8 | 1 | 190 | 4 |
| sana | 3 | 0 | 7 | 228 |

![Matriz de confusión](../ml/outputs/final/confusion_matrix.png)

Por fuente:

| Fuente | Imágenes | Exactitud | F1 macro |
|---|---|---|---|
| bracol | 128 | 0.9844 | 0.9862 |
| decafia | 212 | 0.9953 | 0.9937 |
| rocole | 216 | 0.8565 | 0.7793 |

## Conjunto final: JMuBEN (44297 imágenes)

JMuBEN and JMuBEN2 (Mendeley t2r6rszp5c and tgv3zb82nd, CC BY 4.0): Leaf rust, Healthy, Miner. Cada versión se evaluó con su modelo y su umbral ya confirmados en git.

| Modelo | Exactitud | F1 macro | Recall minador | Recall roya | Recall sana |
|---|---|---|---|---|---|
| v1 (3 clases) | 0.6137 | 0.5895 | 0.3374 | 0.8388 | 0.7619 |
| v2 (3 clases) | 0.8003 | 0.7658 | 0.5458 | 0.8637 | 1.0 |
| v3 (4 clases, actual) | 0.8125 | 0.7806 | 0.5722 | 0.8752 | 1.0 |

El F1 macro se calcula sobre las tres clases que este conjunto contiene. JMuBEN no tiene arañita roja, así que no dice nada sobre esa clase. Este conjunto ya se había usado una vez para medir la v2; no se usó para decidir nada de la v3.

Detalle del modelo actual:

| Clase | Precisión | Recall | F1 | Imágenes |
|---|---|---|---|---|
| arana_roja | 0.0 | 0.0 | 0.0 | 0 |
| minador | 0.965 | 0.5722 | 0.7184 | 16978 |
| roya | 0.517 | 0.8752 | 0.65 | 8336 |
| sana | 0.9481 | 1.0 | 0.9733 | 18983 |

Filas: clase real. Columnas: predicción.

|  | arana_roja | minador | roya | sana |
|---|---|---|---|---|
| arana_roja | 0 | 0 | 0 | 0 |
| minador | 96 | 9714 | 6816 | 352 |
| roya | 0 | 352 | 7296 | 688 |
| sana | 0 | 0 | 0 | 18983 |

JMuBEN son recortes de hojas de café arábica tomados en Kenia y ampliados por sus autores con aumento de datos; no son fotos de campo de una hoja completa.

## Umbral de confianza y calibración

Umbral: **0.6**. Origen: stage1_v3 (holdout source bracol): lowest threshold with accepted accuracy >= 0.90 on a source unseen in training. La regla aplicada a la validación interna daría 0.4, que lo acepta todo.

En el conjunto final, con ese umbral se acepta el 86.7% de las imágenes, con exactitud 0.8528 sobre las aceptadas.

Error de calibración esperado (15 intervalos): 0.0786 en el test interno y 0.0719 en el conjunto final (confianza media 0.7745, exactitud 0.8125).

## Modelo y paridad

| Archivo | Bytes | Entrada | Salida |
|---|---|---|---|
| model_fp32.tflite | 16077592 | [1, 224, 224, 3] float32 | [1, 4] float32 |
| model.tflite | 4573960 | [1, 224, 224, 3] float32 | [1, 4] float32 |

La app lleva `model_fp32.tflite` (copiado a `assets/model.tflite`).

| Comparación (100 imágenes de test) | Coincidencia de clase | Diferencia máx. de probabilidad |
|---|---|---|
| keras vs fp32 | 1.0 | 0.000443 |
| keras vs quantized | 1.0 | 0.157247 |
| fp32 vs quantized | 1.0 | 0.15712 |

## Android (teléfono)

Dispositivo: motorola motorola edge 30, Android 14, arm64-v8a.

- Paridad nivel 1 (modelo aislado): diferencia máxima de probabilidad 0.0000006 (límite 0.01).
- Paridad nivel 2 (flujo completo): 10 de 10 clases coinciden.
- Latencia con 4 hilos (50 medidas): mediana 48.0 ms, p95 49 ms.
- Comparación de hilos: 2 hilos, mediana 48.0 ms y p95 50 ms; 4 hilos, mediana 48.0 ms y p95 49 ms.

## Referencia: modelo v2

EfficientNet-B0 de tres clases (sin arañita roja). Archivos en `ml/outputs/v2_final/`.

## Referencia: modelo v1

MobileNetV2 entrenado con RoCoLe y DECAFIA. Test interno: exactitud 0.9561, F1 macro 0.9587. Ese test estaba sesgado (casi sin imágenes de RoCoLe), así que no es comparable con el test interno de la v2. Archivos en `ml/outputs_v1/`.

## Resultados en campo

NO EJECUTADO. Faltan fotos reales tomadas por el humano en condiciones de campo (fase 12, paso 2). Registrar los casos en `docs/campo.csv` y volver a ejecutar `make results`.

## Limitaciones

- La arañita roja es la clase menos respaldada: una sola fuente (RoCoLe, Robusta de Ecuador), 22 imágenes de test, recall 0.5909 y precisión 0.5417. Ningún conjunto externo la contiene, así que no se sabe cómo generaliza.
- Añadir la arañita roja bajó el acierto en RoCoLe, donde se confunde con roya y con hoja sana (exactitud en RoCoLe: 0.8565).
- El modelo confunde minador con roya en imágenes nuevas: en el conjunto final reconoce 57% de las hojas con minador y solo 52% de lo que llama roya lo es.
- No hay evaluación con fotos de campo tomadas por el equipo. El conjunto final es de otro país y son recortes, no hojas completas fotografiadas con la app.
- BRACOL se deduplicó solo por coincidencia exacta de archivo; si contiene varias tomas de una misma hoja, puede haber fuga entre particiones que infle el test interno.
- Siguen los riesgos de fuga de la v1: recortes de lesión que pueden provenir de fotos de otra partición y varias tomas de una misma hoja en la clase sana de DECAFIA.
- El modelo solo conoce hojas. Una imagen que no es una hoja recibe igualmente una clase.
- La confianza está mal calibrada fuera de los datos de entrenamiento: el modelo se muestra más seguro de lo que acierta.
- Un solo entrenamiento por configuración y una sola semilla: no se midió la variabilidad.
- Cambio de dominio: RoCoLe es Robusta de Ecuador, BRACOL y parte de DECAFIA son de Brasil; en Colombia predomina el arábica.
- Es un prototipo académico de apoyo, no una herramienta de diagnóstico.
