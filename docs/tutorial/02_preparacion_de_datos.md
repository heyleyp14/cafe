# Capítulo 2: Preparación de datos

Cómo se reúnen, etiquetan, limpian y reparten las fotos de hojas antes de entrenar.

## ¿Por qué existe?

Imagine una bodega que recibe café de tres fincas distintas. Cada finca rotula sus sacos a su manera, algunas mandan el mismo saco dos veces (a veces con otra etiqueta) y hay que separar lotes para tres usos: lo que se vende, lo que se guarda para control de calidad y lo que se reserva para la inspección final. Si un mismo saco termina en el lote de venta **y** en el de inspección, la inspección sale engañosamente bien.

Con las fotos ocurre exactamente eso. El modelo aprende con un grupo de fotos (**entrenamiento**), se ajusta mirando otro (**validación**) y se califica con un tercero (**prueba** o *test*). Si una foto, o una copia girada de ella, aparece en entrenamiento y en prueba, el modelo "ya se sabe la respuesta" y la nota es falsa. Una de las reglas del plan lo prohíbe: "No evaluar con imágenes que se usaron para entrenar o elegir hiperparámetros" (`PLAN_Prototipo_Cafe_Kotlin.md`, sección 0).

## La idea principal

El script `ml/01_preparar_datos.py` hace cuatro cosas, en este orden:

1. **Cargar y etiquetar** cada fuente con reglas explícitas (cada dataset nombra sus clases a su manera).
2. **Quitar duplicados** entre todas las fuentes *antes* de dividir, con dos huellas: MD5 (copia exacta del archivo) y dHash (parecido visual).
3. **Agrupar** las fotos que deben ir juntas (por ejemplo, varias fotos de la misma planta).
4. **Repartir** 70/15/15 por grupos, equilibrando cada combinación de **fuente y clase**.

## Cómo funciona en este código

Vive en:
- `ml/01_preparar_datos.py`
- `ml/config.py`
- `ml/tests/test_split.py`
- `docs/decisiones.md` (los motivos de cada regla)
- `docs/resultados.md` (las cifras finales)

### 1. Tres fuentes, tres traductores de etiquetas

Las fuentes son RoCoLe, DECAFIA y BRACOL (citadas en `README.md`). Cada una tiene su "diccionario" hacia las cuatro clases de BioCafe:

```python
ROCOLE_CLASS_MAP = {
    "healthy": "sana",
    "rust_level_1": "roya",
    ...
    "red_spider_mite": "arana_roja",
}
DECAFIA_NAMES = {0: "roya", 1: "coco", 2: "hojas", 3: "minador"}
BRACOL_CLASS_MAP = {0: "sana", 1: "minador", 2: "roya"}
```

DECAFIA no etiqueta la foto entera sino cada lesión con un recuadro. Por eso `decafia_label` aplica la **regla de clase dominante**: cuenta las lesiones de cada tipo (ignora `hojas`, que es solo el contorno), y si no hay lesiones la hoja es `sana`; si gana `coco` o hay empate, la foto se descarta.

```python
counts.pop("hojas", None)
if not counts:
    return "sana", None
ranked = counts.most_common()
if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
    return None, "decafia_tie"
```

`docs/decisiones.md` explica por qué `coco` se descarta: el registro de Zenodo la define como defoliación por gorgojos, que no es ninguna de las clases del modelo.

También se excluyen las fotos de DECAFIA con prefijo `SANAS_ROCOLE` (`DECAFIA_DERIVED_PREFIXES`). Según `docs/decisiones.md`, son 454 copias transformadas de RoCoLe que el hash solo detecta en parte; conservarlas dejaría la misma hoja en particiones distintas.

### 2. Huellas digitales: MD5 y dHash

```python
def fingerprint(path):
    """MD5 of the file plus the dHash of its 8 orientations."""
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    ...
    for mirrored in (False, True):
        base = image.transpose(Image.FLIP_LEFT_RIGHT) if mirrored else image
        for angle in (0, 90, 180, 270):
            small = np.asarray(base.rotate(angle, expand=True).resize((HASH_SIDE + 1, HASH_SIDE), ...))
            hashes.append(np.packbits((small[:, 1:] > small[:, :-1]).flatten()))
```

- **MD5** detecta archivos idénticos byte a byte.
- **dHash** reduce la imagen a 17×16 píxeles en gris y anota, para cada par de vecinos, si el de la derecha es más claro. El resultado (256 bits) cambia poco si la foto se comprime o se reescala. Se calcula en **8 orientaciones** (4 giros × espejo) porque muchas copias estaban rotadas.

Dos umbrales de distancia deciden qué hacer (`docs/decisiones.md`):

```python
DUPLICATE_MAX_DISTANCE = 40  # same picture: keep one copy
RELATED_MAX_DISTANCE = 52  # possible copies or look-alikes: kept, forced into the same split
```

Si las copias de una foto tienen etiquetas distintas, `remove_duplicates` las descarta todas (no sabemos cuál es la correcta). Si coinciden, se conserva una, preferentemente la de RoCoLe, porque trae el identificador de planta.

Para BRACOL solo se usa MD5 (`MD5_ONLY_SOURCES`): según `docs/decisiones.md`, el hash perceptual marcaba como duplicadas 419 de sus 860 imágenes, y al revisarlas a la vista eran hojas distintas sobre el mismo fondo liso.

### 3. Grupos: lo que debe viajar junto

Cada foto tiene un `group`. En RoCoLe es la planta (`C<cultivo>P<planta>` en el nombre del archivo); en las demás, cada foto es su propio grupo. Luego `merge_related_groups` une los grupos de fotos "parecidas" (distancia hasta 52) con una estructura *union-find*, para que caigan en la misma partición.

### 4. El reparto estratificado por fuente y clase

`split_by_group` recorre los grupos (los grandes primero) y manda cada uno entero a la partición que va "más vacía" respecto a su meta en los estratos que contiene:

```python
def fill_after(split):
    return sum(n * (assigned[split][stratum_key] + n) / (fractions[split] * totals[stratum_key])
               for stratum_key, n in strata.items())

best = min(fractions, key=fill_after)
```

El estrato es la pareja `(fuente, clase)`, por ejemplo `rocole/roya`. El docstring explica el porqué: la v1 equilibraba solo por clase, y los grupos grandes de RoCoLe se iban todos a entrenamiento, dejando esa fuente casi fuera de validación y prueba.

Al final, `verify_no_leakage` vuelve a contar fugas sobre el reparto definitivo, y `check_source_balance` detiene el script si algún estrato se aleja más de 0.05 de la meta.

### Lo que salió

Según `docs/resultados.md`: 3736 imágenes en total, 538 duplicados eliminados, desviación máxima respecto a 70/15/15 de 0.0105 y **0** imágenes en dos particiones (por MD5, por hash perceptual y por grupos). La arañita roja solo existe en RoCoLe: 108 imágenes de entrenamiento, 22 de validación y 22 de prueba.

Las imágenes procesadas se guardan reducidas a 512 px de lado mayor (`PROCESSED_MAX_SIDE` en `ml/config.py`) para poder subirlas a Colab; el modelo igual las recibe aplastadas a 224×224, como manda el [contrato](01_contrato_del_modelo.md).

### Las pruebas del reparto

`ml/tests/test_split.py` crea fotos sintéticas (sin imágenes reales) y comprueba que ningún grupo se parta (`test_groups_are_never_split`), que cada estrato quede cerca de la meta, y que el reparto sea determinista con la misma semilla.

## Cómo se conecta

- Respeta el formato que fija [el contrato del modelo](01_contrato_del_modelo.md) (clases y tamaño en `ml/config.py`).
- **Entrega las particiones** al [entrenamiento](03_entrenamiento.md).
- La misma función `split_by_group` se reutiliza para los pliegues de validación cruzada del [capítulo 4](04_evaluacion_umbral_y_duda.md).

## Resumen

La preparación de datos convierte tres fuentes heterogéneas en un conjunto limpio: etiquetas traducidas con reglas explícitas, duplicados quitados entre fuentes antes de dividir, grupos que viajan juntos y un reparto 70/15/15 equilibrado por fuente y clase, verificado sin fugas. Ahora toca enseñarle al modelo con esas fotos.

Ver también: [Glosario](glosario.md)
