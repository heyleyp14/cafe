# Capítulo 4: Evaluación, umbral y regla de duda

Cómo se mide de verdad el modelo, desde qué seguridad se le cree y qué hacer cuando confunde dos clases.

## ¿Por qué existe?

Piense en un estudiante que repasa con los exámenes de años anteriores. Si en el examen final le ponen esas mismas preguntas, saca 10 y no sabemos si aprendió o memorizó. Para saberlo hay que preguntarle cosas nuevas.

Un modelo de aprendizaje automático tiene el mismo problema, agravado: las fotos de prueba suelen venir de las **mismas fuentes** que las de entrenamiento (las mismas cámaras, los mismos fondos, la misma luz). Una nota alta allí no garantiza que funcione con la foto que tome un caficultor en Colombia.

Además, el modelo siempre responde algo, incluso cuando duda. Hay que decidir **desde qué nivel de seguridad se le cree** (el umbral) y **qué hacer con los errores conocidos** (la regla de duda).

## La idea principal

BioCafe mide el modelo en tres escalones, de menos a más exigente:

1. **Test interno**: fotos de prueba de las mismas fuentes del entrenamiento. Útil, pero optimista.
2. **Validación por fuente**: entrenar sin una fuente entera (BRACOL) y medir en ella. Sirve para **elegir** la arquitectura y el umbral.
3. **Conjunto final externo** (JMuBEN): una fuente que nunca se usó para entrenar ni para decidir nada. Se evalúa con el modelo ya congelado.

Y añade dos reglas que la app aplicará:

- **Umbral de confianza**: si la probabilidad más alta es menor que el umbral, la app no afirma ninguna clase.
- **Regla de duda**: si las dos clases más probables son arañita roja y roya, y están demasiado cerca, la app muestra las dos en lugar de elegir una.

## Cómo funciona en este código

Vive en:
- `ml/03_evaluar.py`
- `ml/evaluar_conjunto_final.py`
- `ml/cv_experimentos.py` y `ml/tests/test_cv_folds.py`
- `ml/outputs/final/metrics.json`, `final_holdout.json`, `threshold.json`, `threshold_source.json`, `regla_duda_modelo_final.json`
- `docs/resultados.md` y `docs/decisiones.md`

### Las métricas

`summarize` en `ml/03_evaluar.py` calcula exactitud, precisión, recall y F1 por clase, F1 macro y la matriz de confusión:

```python
precision, recall, f1, support = precision_recall_fscore_support(
    labels, predicted, labels=range(len(CLASSES)), zero_division=0)
matrix = confusion_matrix(labels, predicted, labels=range(len(CLASSES)))
# A source may lack a class (RoCoLe has no minador): the macro average only covers
# the classes that have images, otherwise an absent class would count as F1 = 0.
present = [i for i in range(len(CLASSES)) if support[i] > 0]
```

El comentario es importante: si una clase no tiene imágenes, su F1 vale 0 y hundiría el promedio. Por eso el F1 macro se calcula solo sobre las clases presentes.

### Los resultados, del más optimista al más honesto

Según `docs/resultados.md`:

| Dónde se mide | Imágenes | Exactitud | F1 macro |
|---|---|---|---|
| Test interno | 556 | 0.9388 | 0.8611 |
| Conjunto final (JMuBEN) | 44297 | 0.8125 | 0.7806 (3 clases presentes) |

El propio informe lo dice: "La cifra que estima el comportamiento con imágenes nuevas es la del conjunto final, no la del test interno."

Un detalle que conviene entender: `ml/outputs/final/final_holdout.json` reporta `"f1_macro": 0.5854`. Es la misma evaluación, pero `evaluar_conjunto_final.py` promedia las cuatro clases, incluida `arana_roja`, que JMuBEN no contiene (F1 = 0). `ml/generar_resultados.py` recalcula el promedio sobre las tres clases compartidas (`shared_macro_f1`) y obtiene 0.7806.

La clase más débil es la arañita roja: en el test interno, precisión 0.5417 y recall 0.5909, con solo 22 imágenes (`docs/resultados.md`). En JMuBEN, el modelo reconoce el 57 % de las hojas con minador (recall 0.5722) y solo el 52 % de lo que llama roya lo es (precisión 0.517).

### El umbral: elegido con una fuente no vista

`choose_threshold` barre umbrales de 0.40 a 0.95 y elige el más bajo cuya exactitud sobre las fotos aceptadas llegue a 0.90:

```python
THRESHOLDS = [round(0.40 + 0.05 * i, 2) for i in range(12)]  # 0.40 .. 0.95
TARGET_ACCEPTED_ACCURACY = 0.90
...
for row in sweep:
    if row["accepted_accuracy"] is not None and row["accepted_accuracy"] >= TARGET_ACCEPTED_ACCURACY:
        return row["threshold"], f"lowest threshold reaching the target on {selection}"
```

¿Con qué fotos se hace el barrido? Si la corrida tiene una fuente apartada (`--holdout-source bracol`), con esa fuente; si no, con la validación interna. Aquí está la sutileza que registran `docs/decisiones.md` y `ml/outputs/final/threshold_source.json`: el modelo final se entrena con **todas** las fuentes, así que ya no queda ninguna fuente no vista. La regla aplicada a la validación interna da 0.40, "que lo acepta todo". Por eso el umbral **0.60** se tomó de la corrida `stage1_v3`, donde BRACOL sí era una fuente no vista, y se fijó a mano en `threshold.json`.

Con ese umbral, en JMuBEN se acepta el 86.7 % de las imágenes, con exactitud 0.8528 sobre las aceptadas (`docs/resultados.md`).

### La calibración

`calibration` calcula el error de calibración esperado (ECE) en 15 intervalos: compara la confianza que declara el modelo con lo que realmente acierta. Según `docs/resultados.md`, el ECE es 0.0786 en el test interno y 0.0719 en el conjunto final, donde la confianza media es 0.7745 y la exactitud 0.8125: el modelo se muestra más seguro de lo que acierta.

### La regla de duda entre arañita roja y roya

La matriz de confusión del test interno muestra que la arañita roja se confunde sobre todo con roya. El archivo que lee la app, `ml/outputs/final/threshold.json`, lleva la regla:

```json
{"threshold": 0.6, "model_version": "v3-2026-10", "doubt": {"classes": ["arana_roja", "roya"], "margin": 0.4}}
```

Es decir: hay duda cuando las dos clases más probables son `arana_roja` y `roya` y la diferencia entre sus probabilidades es menor que 0.4. Según `threshold_source.json`, el margen salió de una validación cruzada de 3 pliegues sobre las 3736 imágenes: 0.4 es donde la precisión de la arañita roja afirmada deja de mejorar (de 0.58 a 0.74). La misma nota advierte que se calibró con modelos de validación cruzada de la misma receta, no con el modelo entregado.

`ml/outputs/final/regla_duda_modelo_final.json` mide la regla sobre el modelo entregado, aplicando "doubt rule first, then the 0.6 threshold". En el test interno (556 imágenes), 16 casos quedan en duda: 7 eran errores que se evitan y 9 eran aciertos que se ocultan. La precisión de la arañita roja afirmada sube de 0.5417 (24 afirmaciones sin la regla) a 0.6875 (16 afirmaciones con la regla).

### Validación cruzada: buscar mejoras sin hacer trampa

`ml/cv_experimentos.py` junta todas las imágenes y arma K pliegues con la misma función `split_by_group` del [capítulo 2](02_preparacion_de_datos.md), de modo que cada imagen se prueba exactamente una vez:

```python
def assign_folds(items, folds, seed):
    """Write `item["fold"]` (0..folds-1): group-aware, stratified by (source, class)."""
    prepare.split_by_group(items, fractions={fold: 1 / folds for fold in range(folds)}, seed=seed, key="fold")
```

Prueba cinco variantes (`baseline`, `leafcrop`, `res320`, `boost`, `leafcrop_res320`). La conclusión registrada en `docs/decisiones.md` es que ninguna mejora la arañita roja más allá del margen de azar: es un límite de datos (una sola fuente, con fotos repetidas y etiquetas contradictorias), no de la receta. `ml/tests/test_cv_folds.py` verifica que los grupos nunca crucen pliegues y que cada imagen se pruebe una sola vez.

### El conjunto final se abre una sola vez

`ml/evaluar_conjunto_final.py` empieza con una advertencia: "Nothing measured here may be used to change the model, the threshold or the data." `docs/decisiones.md` registra que modelo, umbral y código se confirmaron en git **antes** de abrir JMuBEN. Eso es lo que hace creíble la cifra 0.8125.

## Cómo se conecta

- Examina el modelo que produce el [entrenamiento](03_entrenamiento.md).
- **Calibra el umbral y la regla de duda** que aplica [la lógica de decisión](07_logica_de_decision.md) en la app.
- Sus JSON alimentan el informe `docs/resultados.md` que genera la [orquestación](10_orquestacion_y_entrega.md).

## Resumen

La evaluación separa cifras optimistas (test interno) de cifras honestas (JMuBEN, una fuente nunca vista), elige el umbral 0.60 con una fuente no vista y define una regla de duda para el par que el modelo confunde. Con el modelo ya examinado, falta llevarlo al teléfono sin cambiar sus respuestas.

Ver también: [Glosario](glosario.md)
