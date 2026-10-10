# Plan de reentrenamiento (modelo v2)

Decidido por el humano el 2026-10-10 tras la validación externa: el modelo v1 obtiene 0.956 de exactitud en su test interno y 0.687 en un dataset externo (BRACOL). Se mantienen las **tres clases** (`minador`, `roya`, `sana`). Este plan amplía el plan original; no lo reemplaza: el contrato de la sección 4 y las reglas de la sección 0 siguen vigentes.

## Objetivo

Un modelo que rinda de forma parecida dentro y fuera de sus datos de entrenamiento, y una evaluación que no engañe. No se promete ninguna cifra: se mide y se reporta.

## Qué se sabe (R0, hecho)

| Hallazgo | Implicación |
|---|---|
| La partición v1 dejó RoCoLe casi fuera de val y test | Hay que estratificar por clase **y** por origen |
| Sustituir el fondo blanco no cambia el resultado en BRACOL | El fondo no es la causa principal |
| Recortar a la hoja empeora y sesga hacia `minador` | El modelo depende del encuadre; hace falta variedad de escala |
| Solo 1 de 860 imágenes externas queda bajo el umbral | El umbral debe elegirse con datos externos |

## Pasos

| Paso | Qué se hace | Criterio de aceptación |
|---|---|---|
| R1. Evaluación | Reparto estratificado por clase y origen, respetando grupos. Reservar un dataset **final intocable** (JMuBEN) que no se usa para entrenar ni para decidir. Validación adicional "por origen": elegir modelo con una fuente que no está en el entrenamiento | Cada origen aparece en train, val y test en proporción parecida; ninguna imagen del conjunto final se abre antes del paso R5 |
| R2. Datos | Sumar BRACOL al entrenamiento. Agrupar por hoja y origen. Muestreo equilibrado por clase y origen | Sin fugas por hash; conteos por clase y origen reportados |
| R3. Robustez | Aumento más fuerte: recortes y escalas aleatorios, color e iluminación, sustitución de fondo cuando se pueda segmentar la hoja | El aumento vive en la tubería de datos, no en el modelo exportado |
| R4. Entrenamiento | Ajuste fino completo, más épocas con parada temprana, suavizado de etiquetas. Comparar MobileNetV2 con EfficientNet-B0. Calibrar la confianza y elegir el umbral con la validación por origen | Se elige por F1 macro en la validación por origen, no en el test interno |
| R5. Cierre | Conversión, paridad, pruebas en emulador y teléfono. Abrir el conjunto final una sola vez | Reporte con las tres cifras: test interno, validación por origen y conjunto final |

## Reglas

- El conjunto final se evalúa **una vez**. Si después se cambia algo por lo que se vio en él, deja de ser final y hay que decirlo.
- El entrenamiento se hace en Colab; lo local es solo para datos, conversión y pruebas.
- Cada paso se registra en `docs/bitacora.md`.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| JMuBEN son recortes aumentados de hojas, no fotos de campo | Declararlo; las fotos de campo del humano siguen siendo la mejor prueba |
| El archivo publicado de BRACOL está truncado (1402 de 1747 imágenes) | Usar lo recuperado y reportar los conteos reales |
| Mejorar en BRACOL por haberlo incluido no demuestra generalización | Por eso existe el conjunto final intocable |
| Sin fotos de campo colombianas, el dominio real sigue sin medirse | Limitación explícita en `docs/resultados.md` |
