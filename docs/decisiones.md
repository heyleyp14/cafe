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
