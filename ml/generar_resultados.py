"""Builds docs/resultados.md from the JSON files under ml/outputs so no figure is typed by hand.

Reports the v2 model (outputs/final), how it was selected (outputs/stage1_*) and the v1
baseline (outputs_v1). Field results come from docs/campo.csv
(columns: foto,clase_real,prediccion,confianza) when the human has filled it in.
"""
import csv
import json

from config import CLASSES, ML_DIR, OUTPUTS_DIR, SPLITS

DOCS_DIR = ML_DIR.parent / "docs"
FIELD_CSV = DOCS_DIR / "campo.csv"
V1_DIR = ML_DIR / "outputs_v1"
V2_DIR = OUTPUTS_DIR / "v2_final"
# Classes shared by every model version and present in the external datasets.
SHARED_CLASSES = ["minador", "roya", "sana"]
FINAL_DIR = OUTPUTS_DIR / "final"
STAGE1_RUNS = {"v2 MobileNetV2 (3 clases)": "stage1_mobilenetv2", "v2 EfficientNet-B0 (3 clases)": "stage1_efficientnetb0",
               "v3 EfficientNet-B0 (4 clases)": "stage1_v3"}


def load(path):
    return json.loads(path.read_text()) if path.exists() else None


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(str(c) for c in row) + " |" for row in rows])


def class_table(per_class):
    return table(["Clase", "Precisión", "Recall", "F1", "Imágenes"],
                 [[c, m["precision"], m["recall"], m["f1"], m["support"]] for c, m in per_class.items()])


def confusion_table(matrix):
    return "Filas: clase real. Columnas: predicción.\n\n" + table(
        ["", *CLASSES], [[c, *row] for c, row in zip(CLASSES, matrix["values"])])


def shared_macro_f1(report):
    """Macro F1 over the classes every version has; a class with no images would drag it to zero."""
    return round(sum(report["per_class"][c]["f1"] for c in SHARED_CLASSES) / len(SHARED_CLASSES), 4)


def shared_recalls(report):
    return [report["per_class"][c]["recall"] for c in SHARED_CLASSES]


def field_section():
    if not FIELD_CSV.exists():
        return ("NO EJECUTADO. Faltan fotos reales tomadas por el humano en condiciones de campo (fase 12, paso 2). "
                "Registrar los casos en `docs/campo.csv` y volver a ejecutar `make results`.")
    rows = list(csv.DictReader(FIELD_CSV.open(encoding="utf-8")))
    correct = sum(r["clase_real"] == r["prediccion"] for r in rows)
    body = table(["Foto", "Clase real", "Predicción", "Confianza"],
                 [[r["foto"], r["clase_real"], r["prediccion"], r["confianza"]] for r in rows])
    return (f"{body}\n\nAciertos: {correct} de {len(rows)} ({correct / len(rows):.1%}). "
            f"**n = {len(rows)} es pequeño**: esta cifra es orientativa y no permite generalizar.")


def main():
    stats = load(OUTPUTS_DIR / "dataset_stats.json")
    history, metrics = load(FINAL_DIR / "history.json"), load(FINAL_DIR / "metrics.json")
    parity, model_io = load(FINAL_DIR / "parity.json"), load(FINAL_DIR / "model_io.json")
    threshold_source = load(FINAL_DIR / "threshold_source.json")
    holdout, holdout_v1 = load(FINAL_DIR / "final_holdout.json"), load(V1_DIR / "final_holdout.json")
    holdout_v2 = load(V2_DIR / "final_holdout.json")
    v1_metrics, v1_external = load(V1_DIR / "metrics.json"), load(V1_DIR / "external_bracol" / "metrics.json")
    stage1 = {name: load(OUTPUTS_DIR / run / "metrics.json") for name, run in STAGE1_RUNS.items()}
    phone = {name: load(FINAL_DIR / "android_phone" / f"{name}.json")
             for name in ("latency", "latency_threads", "parity_level1", "parity_level2")}

    internal, training = metrics["internal"], history["training"]
    val_loss = history["head"]["val_loss"] + history["finetune"]["val_loss"]
    sources = sorted(stats["counts_by_source"]["train"])

    parts = [
        "# Resultados",
        "Archivo generado por `ml/generar_resultados.py` a partir de `ml/outputs/`. No editar a mano.",
        f"Modelo `{metrics['model_version']}`: {training['arch']} con clases {', '.join(CLASSES)}.",

        "## Lo esencial",
        table(["Dónde se mide", "Qué mide", "Imágenes", "Exactitud", "F1 macro"], [
            ["Test interno", "Imágenes de las mismas fuentes del entrenamiento", internal["images"],
             internal["accuracy"], internal["f1_macro"]],
            ["Conjunto final (JMuBEN)", "Fuente nunca usada para entrenar ni para decidir", holdout["images"],
             f"**{holdout['accuracy']}**", f"**{shared_macro_f1(holdout)}** (3 clases presentes)"],
        ]),
        "La cifra que estima el comportamiento con imágenes nuevas es la del conjunto final, no la del test interno.",

        "## Datos",
        table(["Fuente y clase", *SPLITS], [
            [f"{source} / {label}", *[stats["counts_by_source"][split][source].get(label, 0) for split in SPLITS]]
            for source in sources for label in CLASSES
            if any(stats["counts_by_source"][split][source].get(label, 0) for split in SPLITS)]),
        f"Total: {stats['final_images']} imágenes. Reparto estratificado por fuente y clase; desviación máxima "
        f"respecto a 70/15/15: {stats['source_balance_check']['worst_deviation']}. Duplicados eliminados: "
        f"{stats['duplicates']['duplicates_removed']}. Imágenes en dos particiones: "
        f"{stats['leakage_check']['md5_in_two_splits']} por MD5, "
        f"{stats['leakage_check']['perceptual_pairs_in_two_splits']} pares por hash perceptual y "
        f"{stats['leakage_check']['groups_in_two_splits']} grupos repartidos.",

        "## Entrenamiento del modelo final",
        f"Hardware: {', '.join(training['gpu']) or 'CPU'}. Tiempo: {training['seconds']} s. Épocas ejecutadas: "
        f"{training['epochs_run']['head']} (cabeza) + {training['epochs_run']['finetune']} (ajuste fino). "
        f"TensorFlow {training['tensorflow']}, Keras {training['keras']}, Python {training['python']}. "
        f"Pérdida de validación: {val_loss[0]:.4f} en la época 1, mínimo {min(val_loss):.4f}.",

        "## Cómo se eligió la arquitectura (etapa 1)",
        "Cada modelo de esta tabla se entrenó sin BRACOL y se midió en BRACOL, una fuente que no había visto. El F1 "
        "macro es sobre las tres clases que BRACOL contiene.",
        table(["Modelo", "BRACOL exactitud", "BRACOL F1 macro", "Recall minador", "Recall roya", "Recall sana"], [
            ["v1 MobileNetV2 (3 clases)", v1_external["accuracy"], v1_external["f1_macro"], *shared_recalls(v1_external)],
            *[[name, m["holdout_source"]["accuracy"], shared_macro_f1(m["holdout_source"]),
               *shared_recalls(m["holdout_source"])] for name, m in stage1.items()],
        ]),
        "BRACOL se usó para elegir la arquitectura y el umbral, y después se añadió al entrenamiento del modelo "
        "final; por eso sus cifras no son una estimación independiente.",

        f"## Test interno ({internal['images']} imágenes)",
        f"Exactitud: {internal['accuracy']}. F1 macro: {internal['f1_macro']}.",
        class_table(internal["per_class"]),
        confusion_table(internal["confusion_matrix"]),
        "![Matriz de confusión](../ml/outputs/final/confusion_matrix.png)",
        "Por fuente:",
        table(["Fuente", "Imágenes", "Exactitud", "F1 macro"],
              [[s, m["images"], m["accuracy"], m["f1_macro"]] for s, m in sorted(metrics["by_source"].items())]),

        f"## Conjunto final: JMuBEN ({holdout['images']} imágenes)",
        f"{holdout['dataset']}. Cada versión se evaluó con su modelo y su umbral ya confirmados en git.",
        table(["Modelo", "Exactitud", "F1 macro", "Recall minador", "Recall roya", "Recall sana"], [
            ["v1 (3 clases)", holdout_v1["accuracy"], shared_macro_f1(holdout_v1), *shared_recalls(holdout_v1)],
            ["v2 (3 clases)", holdout_v2["accuracy"], shared_macro_f1(holdout_v2), *shared_recalls(holdout_v2)],
            ["v3 (4 clases, actual)", holdout["accuracy"], shared_macro_f1(holdout), *shared_recalls(holdout)],
        ]),
        "El F1 macro se calcula sobre las tres clases que este conjunto contiene. JMuBEN no tiene arañita roja, así "
        "que no dice nada sobre esa clase. Este conjunto ya se había usado una vez para medir la v2; no se usó para "
        "decidir nada de la v3.",
        "Detalle del modelo actual:",
        class_table(holdout["per_class"]),
        confusion_table(holdout["confusion_matrix"]),
        "JMuBEN son recortes de hojas de café arábica tomados en Kenia y ampliados por sus autores con aumento de "
        "datos; no son fotos de campo de una hoja completa.",

        "## Umbral de confianza y calibración",
        f"Umbral: **{threshold_source['threshold']}**. Origen: {threshold_source['chosen_from']}. La regla aplicada a "
        f"la validación interna daría {threshold_source['internal_validation_rule_would_give']}, que lo acepta todo.",
        f"En el conjunto final, con ese umbral se acepta el {holdout['at_threshold']['accepted_fraction']:.1%} de "
        f"las imágenes, con exactitud {holdout['at_threshold']['accepted_accuracy']} sobre las aceptadas.",
        f"Error de calibración esperado (15 intervalos): {metrics['calibration']['internal_test']['expected_calibration_error']} "
        f"en el test interno y {holdout['expected_calibration_error']} en el conjunto final (confianza media "
        f"{holdout['mean_confidence']}, exactitud {holdout['accuracy']}).",

        "## Modelo y paridad",
        table(["Archivo", "Bytes", "Entrada", "Salida"],
              [[m["file"], m["bytes"], f"{m['inputs'][0]['shape']} {m['inputs'][0]['dtype']}",
                f"{m['outputs'][0]['shape']} {m['outputs'][0]['dtype']}"]
               for k, m in model_io.items() if k != "contract_ok"]),
        f"La app lleva `{parity['golden']['model']}` (copiado a `assets/model.tflite`).",
        table(["Comparación (100 imágenes de test)", "Coincidencia de clase", "Diferencia máx. de probabilidad"],
              [[k.replace("_", " "), parity[k]["argmax_agreement"], parity[k]["max_abs_probability_difference"]]
               for k in ("keras_vs_fp32", "keras_vs_quantized", "fp32_vs_quantized")]),

        "## Android (teléfono)",
        f"Dispositivo: {phone['latency']['device']}, Android {phone['latency']['android']}, {phone['latency']['abi']}.",
        "\n".join([
            f"- Paridad nivel 1 (modelo aislado): diferencia máxima de probabilidad "
            f"{max(phone['parity_level1'].values()):.7f} (límite 0.01).",
            f"- Paridad nivel 2 (flujo completo): {phone['parity_level2']['matches']} de "
            f"{phone['parity_level2']['images']} clases coinciden.",
            f"- Latencia con {phone['latency']['threads']} hilos ({phone['latency']['measured_runs']} medidas): "
            f"mediana {phone['latency']['median_ms']} ms, p95 {phone['latency']['p95_ms']} ms.",
            "- Comparación de hilos: " + "; ".join(
                f"{k.split('_')[1]} hilos, mediana {v['median_ms']} ms y p95 {v['p95_ms']} ms"
                for k, v in phone["latency_threads"].items() if k.startswith("threads_")) + ".",
        ]),

        "## Referencia: modelo v2",
        "EfficientNet-B0 de tres clases (sin arañita roja). Archivos en `ml/outputs/v2_final/`.",
        "## Referencia: modelo v1",
        f"MobileNetV2 entrenado con RoCoLe y DECAFIA. Test interno: exactitud {v1_metrics['test']['accuracy']}, "
        f"F1 macro {v1_metrics['test']['f1_macro']}. Ese test estaba sesgado (casi sin imágenes de RoCoLe), así que "
        "no es comparable con el test interno de la v2. Archivos en `ml/outputs_v1/`.",

        "## Resultados en campo",
        field_section(),

        "## Limitaciones",
        "\n".join("- " + line for line in [
            f"La arañita roja es la clase menos respaldada: una sola fuente (RoCoLe, Robusta de Ecuador), "
            f"{internal['per_class']['arana_roja']['support']} imágenes de test, recall "
            f"{internal['per_class']['arana_roja']['recall']} y precisión {internal['per_class']['arana_roja']['precision']}. "
            "Ningún conjunto externo la contiene, así que no se sabe cómo generaliza.",
            "Añadir la arañita roja bajó el acierto en RoCoLe, donde se confunde con roya y con hoja sana "
            f"(exactitud en RoCoLe: {metrics['by_source']['rocole']['accuracy']}).",
            "El modelo confunde minador con roya en imágenes nuevas: en el conjunto final reconoce "
            f"{holdout['per_class']['minador']['recall']:.0%} de las hojas con minador y solo "
            f"{holdout['per_class']['roya']['precision']:.0%} de lo que llama roya lo es.",
            "No hay evaluación con fotos de campo tomadas por el equipo. El conjunto final es de otro país y son "
            "recortes, no hojas completas fotografiadas con la app.",
            "BRACOL se deduplicó solo por coincidencia exacta de archivo; si contiene varias tomas de una misma "
            "hoja, puede haber fuga entre particiones que infle el test interno.",
            "Siguen los riesgos de fuga de la v1: recortes de lesión que pueden provenir de fotos de otra partición "
            "y varias tomas de una misma hoja en la clase sana de DECAFIA.",
            "El modelo solo conoce hojas. Una imagen que no es una hoja recibe igualmente una clase.",
            "La confianza está mal calibrada fuera de los datos de entrenamiento: el modelo se muestra más seguro de "
            "lo que acierta.",
            "Un solo entrenamiento por configuración y una sola semilla: no se midió la variabilidad.",
            "Cambio de dominio: RoCoLe es Robusta de Ecuador, BRACOL y parte de DECAFIA son de Brasil; en Colombia "
            "predomina el arábica.",
            "Es un prototipo académico de apoyo, no una herramienta de diagnóstico.",
        ]),
    ]
    (DOCS_DIR / "resultados.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print("docs/resultados.md escrito")


if __name__ == "__main__":
    main()
