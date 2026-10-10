"""Builds docs/resultados.md from ml/outputs/*.json so no figure is typed by hand.

Field results are read from docs/campo.csv (columns: foto,clase_real,prediccion,confianza)
when the human has filled it in; otherwise that section says NO EJECUTADO.
"""
import csv
import json

from config import CLASSES, ML_DIR, OUTPUTS_DIR, SPLITS

DOCS_DIR = ML_DIR.parent / "docs"
FIELD_CSV = DOCS_DIR / "campo.csv"


def load(name):
    path = OUTPUTS_DIR / name
    return json.loads(path.read_text()) if path.exists() else None


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(str(c) for c in row) + " |" for row in rows])


def field_section():
    if not FIELD_CSV.exists():
        return ("NO EJECUTADO. Falta instalar el APK en un teléfono y probar con fotos reales tomadas por el "
                "humano (fase 12). Registrar los casos en `docs/campo.csv` y volver a ejecutar `make results`.")
    rows = list(csv.DictReader(FIELD_CSV.open(encoding="utf-8")))
    correct = sum(r["clase_real"] == r["prediccion"] for r in rows)
    body = table(["Foto", "Clase real", "Predicción", "Confianza"],
                 [[r["foto"], r["clase_real"], r["prediccion"], r["confianza"]] for r in rows])
    return (f"{body}\n\nAciertos: {correct} de {len(rows)} ({correct / len(rows):.1%}). "
            f"**n = {len(rows)} es pequeño**: esta cifra es orientativa y no permite generalizar.")


def main():
    stats, history, metrics = load("dataset_stats.json"), load("history.json"), load("metrics.json")
    parity, model_io = load("parity.json"), load("model_io.json")
    latency, threads = load("android_emulator/latency.json"), load("android_emulator/latency_threads.json")
    level1, level2 = load("android_emulator/parity_level1.json"), load("android_emulator/parity_level2.json")
    test, threshold, training = metrics["test"], metrics["threshold"], history["training"]
    val_loss = history["head"]["val_loss"] + history["finetune"]["val_loss"]

    parts = [
        "# Resultados",
        "Archivo generado por `ml/generar_resultados.py` a partir de `ml/outputs/`. No editar a mano.",
        f"Modelo `{metrics['model_version']}`: MobileNetV2 con clases {', '.join(CLASSES)}.",
        "## Datos",
        table(["Clase", *SPLITS, "Total"],
              [[c, *[stats["counts"][s][c] for s in SPLITS], stats["per_class_total"][c]] for c in CLASSES]),
        f"Total: {stats['final_images']} imágenes. Desbalance en entrenamiento (clase mayor / menor): "
        f"{stats['imbalance_ratio_train']}. Duplicados eliminados: {stats['duplicates']['duplicates_removed']}. "
        f"Imágenes en dos particiones: {stats['leakage_check']['md5_in_two_splits']} por MD5, "
        f"{stats['leakage_check']['perceptual_pairs_in_two_splits']} pares por hash perceptual y "
        f"{stats['leakage_check']['groups_in_two_splits']} grupos repartidos.",
        "## Entrenamiento",
        f"Hardware: {', '.join(training['gpu']) or 'CPU'}. Tiempo: {training['seconds']} s. "
        f"Épocas ejecutadas: {training['epochs_run']['head']} (cabeza) + {training['epochs_run']['finetune']} "
        f"(ajuste fino). TensorFlow {training['tensorflow']}, Keras {training['keras']}, Python {training['python']}. "
        f"Pérdida de validación: {val_loss[0]:.4f} en la época 1, mínimo {min(val_loss):.4f}.",
        f"## Métricas en test ({test['images']} imágenes)",
        f"Exactitud: {test['accuracy']}. **F1 macro: {test['f1_macro']}**.",
        table(["Clase", "Precisión", "Recall", "F1", "Imágenes"],
              [[c, m["precision"], m["recall"], m["f1"], m["support"]] for c, m in test["per_class"].items()]),
        "### Matriz de confusión",
        "Filas: clase real. Columnas: predicción.",
        table(["", *CLASSES], [[c, *row] for c, row in zip(CLASSES, test["confusion_matrix"]["values"])]),
        "![Matriz de confusión](../ml/outputs/confusion_matrix.png)",
        "## Umbral de confianza: cobertura frente a exactitud",
        f"Umbral elegido en validación: **{threshold['chosen']}** (regla: menor umbral con exactitud aceptada "
        f"≥ {threshold['target_accepted_accuracy']}). Exactitud en validación sin umbral: "
        f"{threshold['validation_accuracy_without_threshold']}.",
        table(["Umbral", "Aceptadas", "Fracción aceptada", "Exactitud en aceptadas"],
              [[r["threshold"], r["accepted"], r["accepted_fraction"], r["accepted_accuracy"]]
               for r in threshold["validation_sweep"]]),
        f"En test, con el umbral elegido: se acepta {threshold['test_at_chosen']['accepted_fraction']:.1%} "
        f"de las imágenes, con exactitud {threshold['test_at_chosen']['accepted_accuracy']}.",
        "## Modelo y paridad",
        table(["Archivo", "Bytes", "Entrada", "Salida"],
              [[m["file"], m["bytes"], f"{m['inputs'][0]['shape']} {m['inputs'][0]['dtype']}",
                f"{m['outputs'][0]['shape']} {m['outputs'][0]['dtype']}"]
               for k, m in model_io.items() if k != "contract_ok"]),
        f"La app lleva `{parity['golden']['model']}` (copiado a `assets/model.tflite`).",
        table(["Comparación (100 imágenes de test)", "Coincidencia de clase", "Diferencia máx. de probabilidad"],
              [[k.replace("_", " "), parity[k]["argmax_agreement"], parity[k]["max_abs_probability_difference"]]
               for k in ("keras_vs_fp32", "keras_vs_quantized", "fp32_vs_quantized")]),
        "## Android (emulador, no es un teléfono)",
        f"Dispositivo: {latency['device']}, Android {latency['android']}, {latency['abi']}.",
        f"- Paridad nivel 1 (modelo aislado): diferencia máxima de probabilidad {max(level1.values()):.7f} "
        "(límite 0.01).",
        f"- Paridad nivel 2 (flujo completo): {level2['matches']} de {level2['images']} clases coinciden.",
        f"- Latencia con {latency['threads']} hilos ({latency['measured_runs']} medidas): mediana "
        f"{latency['median_ms']} ms, p95 {latency['p95_ms']} ms.",
        "- Comparación de hilos: " + "; ".join(
            f"{k.split('_')[1]} hilos, mediana {v['median_ms']} ms y p95 {v['p95_ms']} ms"
            for k, v in threads.items() if k.startswith("threads_")) + ".",
        "## Resultados en campo",
        field_section(),
        "## Limitaciones",
        "\n".join("- " + line for line in [
            "Las métricas se midieron con imágenes de los mismos datasets usados para entrenar (RoCoLe y DECAFIA); "
            "no miden el rendimiento con fotos nuevas.",
            "Posible fuga entre particiones que el hash no detecta: recortes de lesión que pueden provenir de fotos "
            "de otra partición y varias tomas de una misma hoja en la clase sana. Tiende a inflar las métricas.",
            "Casi todas las imágenes de minador son hojas sobre fondo blanco y casi todas las sanas son de campo: "
            "el modelo puede apoyarse en el fondo.",
            "El modelo solo conoce hojas. Una imagen que no es una hoja recibe igualmente una clase con confianza "
            "alta; en el emulador, una sala se clasificó como hoja sana.",
            "Con el umbral elegido se aceptan todas las imágenes de validación y de test, así que en la práctica "
            "no filtra.",
            "Cambio de dominio: RoCoLe es café Robusta de Ecuador y parte de DECAFIA proviene de Brasil; en "
            "Colombia predomina el arábica.",
            "La clase minador tiene pocas imágenes de test, por lo que sus métricas son poco precisas.",
            "Las latencias son de un emulador en un PC, no de un teléfono.",
            "Es un prototipo académico de apoyo, no una herramienta de diagnóstico.",
        ]),
    ]
    (DOCS_DIR / "resultados.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print("docs/resultados.md escrito")


if __name__ == "__main__":
    main()
