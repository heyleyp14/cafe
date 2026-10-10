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
- **Decisión:** se excluyen los recortes `COCO_RECORTE_*`, `MINADO_RECORTES_*` y `ROYA_RECORTES_*` (398).
- **Motivo:** son acercamientos de la lesión, no hojas completas. No corresponden a la entrada de la app (una hoja completa) y podrían ser recortes de fotos presentes en otra partición, algo que un hash no detecta. **Es una decisión propia, no del plan, y es reversible** (constante `DECAFIA_CROP_PREFIXES` en `ml/01_preparar_datos.py`). Costo: menos imágenes de `minador` y `roya`.

## 2026-10-10 — Fase 1: duplicados y agrupación

- **Decisión:** hash perceptual dHash de 256 bits, comparado sobre las 8 orientaciones (rotaciones y espejos) de cada imagen, además de MD5.
  - Distancia ≤ 40: se considera la misma foto y se conserva una sola copia (la de RoCoLe si existe). Si las copias tienen etiquetas distintas, se descartan todas.
  - Distancia 41–52: se conservan, pero se obligan a caer en la misma partición.
- **Motivo:** los umbrales se eligieron mirando pares de muestra por distancia. Hasta ~45 los pares eran la misma foto (a menudo rotada); a partir de ~53 eran hojas distintas sobre fondo blanco. Un primer intento con dHash de 64 bits daba falsos duplicados y se desechó.
- **Decisión:** las fotos de RoCoLe de la misma planta (`C<cultivo>P<planta>` en el nombre) van juntas a una sola partición.
- **Decisión:** se ignora la partición original de DECAFIA y se divide de nuevo 70/15/15 con semilla 42, estratificado por clase y respetando los grupos.
