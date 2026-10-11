import json, re, shutil, struct, sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path("/home/josue/Documentos/Cursos/proyecto"); S = Path(sys.argv[1]); UN = S / "doc" / "un"
doc_path = UN / "word" / "document.xml"; x = doc_path.read_text(encoding="utf8")
J = lambda p: json.loads((ROOT / p).read_text())
final, hold, hold_v2, hold_v1 = J("ml/outputs/final/metrics.json"), J("ml/outputs/final/final_holdout.json"), J("ml/outputs/v2_final/final_holdout.json"), J("ml/outputs_v1/final_holdout.json")
stats, hist, parity, duda = J("ml/outputs/dataset_stats.json"), J("ml/outputs/final/history.json"), J("ml/outputs/final/parity.json"), J("ml/outputs/final/regla_duda_modelo_final.json")
phone = J("ml/outputs/final/android_phone/latency.json"); threads = J("ml/outputs/final/android_phone/latency_threads.json")
cv = {v: J(f"ml/outputs/cv/{v}.json") for v in ("baseline_corrida1", "leafcrop", "boost", "res320", "leafcrop_res320")}
C = ["arana_roja", "minador", "roya", "sana"]; NOMBRE = {"arana_roja": "Arañita roja", "minador": "Minador", "roya": "Roya", "sana": "Hoja sana"}
f4 = lambda v: f"{v:.4f}".replace(".", ","); f3 = lambda v: f"{v:.3f}".replace(".", ",")
macro3 = lambda r: sum(r["per_class"][c]["f1"] for c in ("minador", "roya", "sana")) / 3

RUN = '<w:r><w:rPr>{b}<w:rtl w:val="0"/></w:rPr><w:t xml:space="preserve">{t}</w:t></w:r>'
B = '<w:b w:val="1"/><w:bCs w:val="1"/>'
def run(t, bold=False): return RUN.format(b=B if bold else "", t=escape(t))
def body(t): return f'<w:p><w:pPr><w:spacing w:after="200" w:lineRule="auto"/><w:jc w:val="both"/><w:rPr/></w:pPr>{run(t)}</w:p>'
def head(t): return f'<w:p><w:pPr><w:keepNext w:val="1"/><w:spacing w:after="200" w:lineRule="auto"/><w:jc w:val="both"/><w:rPr>{B}</w:rPr></w:pPr>{run(t, True)}</w:p>'
def objective(t): return f'<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="7"/></w:numPr><w:spacing w:after="200" w:lineRule="auto"/><w:ind w:left="720" w:hanging="360"/><w:jc w:val="both"/><w:rPr>{B}</w:rPr></w:pPr>{run(t, True)}</w:p>'
def caption(t): return f'<w:p><w:pPr><w:spacing w:after="200" w:lineRule="auto"/><w:jc w:val="center"/><w:rPr><w:sz w:val="20"/></w:rPr></w:pPr><w:r><w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/><w:rtl w:val="0"/></w:rPr><w:t xml:space="preserve">{escape(t)}</w:t></w:r></w:p>'
def ref(t): return f'<w:p><w:pPr><w:spacing w:after="200" w:lineRule="auto"/><w:jc w:val="left"/><w:rPr/></w:pPr>{run(t)}</w:p>'
BORD = "".join(f'<w:{s} w:color="000000" w:space="0" w:sz="8" w:val="single"/>' for s in ("top", "left", "bottom", "right"))
def cell(t, w, bold=False, center=True):
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders>{BORD}</w:tcBorders><w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar><w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:after="0" w:lineRule="auto"/><w:jc w:val="{"center" if center else "left"}"/><w:rPr><w:sz w:val="20"/></w:rPr></w:pPr><w:r><w:rPr>{B if bold else ""}<w:sz w:val="20"/><w:szCs w:val="20"/><w:rtl w:val="0"/></w:rPr><w:t xml:space="preserve">{escape(str(t))}</w:t></w:r></w:p></w:tc>')
def table(headers, rows, widths):
    assert sum(widths) == 9360 and all(len(r) == len(widths) for r in rows)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    trs = ['<w:tr><w:trPr><w:cantSplit w:val="1"/><w:tblHeader w:val="1"/></w:trPr>' + "".join(cell(h, w, True) for h, w in zip(headers, widths)) + "</w:tr>"]
    for r in rows: trs.append('<w:tr><w:trPr><w:cantSplit w:val="1"/></w:trPr>' + "".join(cell(v, w, False, k > 0) for k, (v, w) in enumerate(zip(r, widths))) + "</w:tr>")
    return (f'<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/><w:tblLook w:val="0600"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>'
            '<w:p><w:pPr><w:spacing w:after="120" w:lineRule="auto"/><w:rPr/></w:pPr></w:p>')

# images
rels_path = UN / "word" / "_rels" / "document.xml.rels"; rels = rels_path.read_text(encoding="utf8")
next_rid = max(int(i) for i in re.findall(r'Id="rId(\d+)"', rels)) + 1; pic_id = [900000001]; new_rels = []
def png_size(p):
    d = p.read_bytes(); return struct.unpack(">II", d[16:24])
def image(src, name, width_emu):
    global next_rid
    dst = UN / "word" / "media" / name; shutil.copyfile(src, dst); w, h = png_size(dst); cx, cy = width_emu, int(width_emu * h / w)
    rid = f"rId{next_rid}"; next_rid += 1; new_rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>')
    pid = pic_id[0]; pic_id[0] += 1
    return (f'<w:r><w:rPr/><w:drawing><wp:inline distB="0" distT="0" distL="57150" distR="57150"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent b="0" l="0" r="0" t="0"/><wp:docPr id="{pid}" name="{name}"/>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{name}"/><pic:cNvPicPr preferRelativeResize="0"/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:srcRect b="0" l="0" r="0" t="0"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"/><a:ln/></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
def figure(*runs): return f'<w:p><w:pPr><w:keepNext w:val="1"/><w:spacing w:after="80" w:lineRule="auto"/><w:jc w:val="center"/><w:rPr/></w:pPr>{"".join(runs)}</w:p>'

it, tr = final["internal"], hist["training"]; cs = stats["counts"]; tot = {c: sum(cs[s][c] for s in cs) for c in C}
src = {s: sum(sum(stats["counts_by_source"][sp].get(s, {}).values()) for sp in cs) for s in ("rocole", "decafia", "bracol")}
P = []
# ---------------- Objetivo 3
P += [objective("Construir un sistema que integre modelos de redes neuronales convolucionales con técnicas de procesamiento paralelo y aceleración CUDA para la detección de plagas y enfermedades."),
 body("Para dar cumplimiento a este objetivo se construyó BioCafe, un prototipo compuesto por dos partes que se desarrollaron por separado y luego se integraron: un flujo de entrenamiento escrito en Python, que prepara las imágenes, entrena y evalúa el modelo, y una aplicación móvil para Android escrita en Kotlin, que ejecuta el modelo dentro del teléfono sin conexión a internet. Ambas partes se comunican mediante un contrato fijo: la imagen entra al modelo como un tensor de 224 × 224 píxeles en formato RGB con valores de 0 a 255, la normalización ocurre dentro del modelo y la salida es una probabilidad por cada clase."),
 head("3.1 Preparación de los datos"),
 body(f"A partir del análisis de viabilidad del primer objetivo, el sistema se limitó a afectaciones visibles en la hoja y con imágenes públicas disponibles: roya, minador de las hojas y arañita roja, además de la hoja sana. Se integraron tres conjuntos de datos con licencia CC BY 4.0: RoCoLe [39] ({src['rocole']} imágenes tras la depuración), DECAFIA [40] ({src['decafia']}) y BRACOL [41] ({src['bracol']}). Al revisar DECAFIA se encontró que su categoría «coco» corresponde a defoliación por gorgojos, por lo que no se utilizó, y que el conjunto contiene 2769 imágenes y no las 2786 que anuncia su descripción."),
 body(f"La preparación se automatizó en un script que traduce las etiquetas de cada fuente a las cuatro clases del sistema, elimina imágenes duplicadas y reparte los datos en entrenamiento (70 %), validación (15 %) y prueba (15 %). La detección de duplicados combina la suma MD5 con un hash perceptual de 256 bits comparado en las ocho orientaciones de cada imagen, ya que varias copias estaban giradas o reflejadas; se eliminaron {stats['duplicates']['duplicates_removed']} duplicados y se descartaron {stats['duplicates']['duplicates_conflicting_labels']} imágenes repetidas con etiquetas contradictorias. El reparto se hace por grupos, de modo que las fotografías de una misma planta nunca quedan en particiones distintas, y se estratifica por fuente y por clase. Esta última condición se añadió tras detectar que una primera versión del reparto dejaba casi todas las imágenes de RoCoLe en el entrenamiento y muy pocas en la prueba, lo que hacía poco fiables las métricas. El resultado final son {stats['final_images']} imágenes, sin ninguna repetida entre particiones."),
 table(["Clase", "Entrenamiento", "Validación", "Prueba", "Total"], [[NOMBRE[c], cs["train"][c], cs["val"][c], cs["test"][c], tot[c]] for c in C] + [["Total", sum(cs["train"].values()), sum(cs["val"].values()), sum(cs["test"].values()), stats["final_images"]]], [2760, 1800, 1600, 1600, 1600]),
 caption("Distribución de las imágenes por clase y partición."),
 head("3.2 Entrenamiento del modelo con aceleración CUDA"),
 body("El modelo se entrenó en Google Colab sobre una GPU NVIDIA Tesla T4, con TensorFlow 2.21 y Keras 3. Durante el entrenamiento, CUDA paraleliza en la GPU las operaciones de convolución y de álgebra matricial de la red, que es la parte del proceso con mayor costo de cómputo. Se empleó aprendizaje por transferencia: se parte de una red preentrenada en ImageNet y se entrena en dos etapas, primero la capa de clasificación con la base congelada y después un ajuste fino de toda la red con una tasa de aprendizaje menor, manteniendo congeladas las capas de normalización por lotes. El aumento de datos (rotaciones, acercamientos, traslaciones y cambios de brillo, contraste, tono y saturación) se aplica solo en la tubería de datos y no forma parte del modelo exportado."),
 body("En el segundo objetivo se había señalado MobileNet como la alternativa más adecuada. Para comprobarlo se entrenaron MobileNetV2 y EfficientNet-B0 [44] con RoCoLe y DECAFIA y se midieron en BRACOL, una fuente que ninguno de los dos había visto. EfficientNet-B0 obtuvo un F1 macro de 0,8494 frente a 0,7313 de MobileNetV2, por lo que se adoptó como arquitectura del sistema, a costa de un modelo más pesado y más lento. El modelo final, de cuatro clases y entrenado con las tres fuentes, requirió " + f"{tr['seconds']:.0f}".replace(".", ",") + f" segundos (unos 28 minutos): {tr['epochs_run']['head']} épocas de la primera etapa y {tr['epochs_run']['finetune']} de ajuste fino, detenido por parada temprana."),
 head("3.3 Integración en el dispositivo móvil"),
 body("El modelo entrenado se convirtió al formato TensorFlow Lite y se ejecuta en el teléfono con el motor LiteRT, que reparte las operaciones entre varios hilos de la CPU. Se generaron dos versiones: una sin cuantizar de 16,1 MB" + " y otra con cuantización de rango dinámico de 4,6 MB. Se entrega la primera porque, en las pruebas hechas con una versión anterior del modelo, la variante cuantizada produjo probabilidades distintas según el procesador (diferencias de hasta 0,015 respecto a la referencia en un emulador), mientras que la variante sin cuantizar coincidió con el modelo original."),
 body("La aplicación se desarrolló en Kotlin con Jetpack Compose para la interfaz y CameraX para la cámara, siguiendo una arquitectura MVVM con una sola actividad. El usuario toma una fotografía o la elige de la galería; la aplicación la endereza, la reduce y la entrega al modelo, y muestra la clase más probable, la confianza, las tres clases con mayor probabilidad y una ficha con los síntomas y las condiciones favorables descritos en el primer objetivo. La aplicación no solicita permiso de acceso a internet, de modo que las imágenes no salen del dispositivo."),
 figure(image(S / "web_inicio.png", "biocafe_inicio.png", 1463040), image(S / "web_resultado.png", "biocafe_resultado.png", 1463040), image(S / "duda.png", "biocafe_duda.png", 1463040)),
 caption("Pantallas de BioCafe: inicio, resultado y aviso de duda entre dos afectaciones."),
 body("Sobre la salida del modelo se aplican dos reglas. Si ninguna clase alcanza una confianza de 0,60, la aplicación indica que no se pudo determinar con seguridad y ofrece consejos de captura. Si las dos clases más probables son arañita roja y roya y su diferencia es menor de 0,40, muestra ambas posibilidades con sus síntomas en lugar de afirmar una sola. Los dos valores se obtuvieron a partir de datos de evaluación, como se describe en el siguiente objetivo."),
 head("3.4 Alcance respecto a lo planteado"),
 body("El procesamiento paralelo del sistema se concreta en dos puntos: la aceleración con CUDA durante el entrenamiento en GPU y la ejecución con varios hilos de CPU durante la inferencia en el teléfono. No se utilizaron OpenMP ni MPI, porque los marcos de trabajo empleados ya resuelven la paralelización en ambos casos. Tampoco se implementó la segmentación con Mask R-CNN analizada en el segundo objetivo: el sistema clasifica la imagen completa, y la segmentación queda como trabajo futuro, pensada para ejecutarse en un servidor por su costo de cómputo. Las afectaciones que se manifiestan en el fruto o en la raíz, como la broca y las cochinillas, quedaron fuera por lo expuesto en el análisis de viabilidad."),
]
# ---------------- Objetivo 4
ar = it["per_class"]["arana_roja"]
P += [objective("Evaluar el desempeño del sistema mediante imágenes de prueba y métricas de precisión, sensibilidad y tiempo de procesamiento para la validación de su funcionamiento en la detección de las afectaciones seleccionadas."),
 body("La evaluación se organizó en tres niveles, de menor a mayor exigencia: un conjunto de prueba interno, con imágenes de las mismas fuentes usadas para entrenar pero que el modelo no vio; una fuente apartada del entrenamiento, usada para elegir la arquitectura y el umbral; y un conjunto externo, JMuBEN [42], [43], con imágenes de café arábica tomadas en Kenia que no intervinieron en ninguna decisión. Se reportan la exactitud, la precisión, la sensibilidad (recall) y el F1 por clase, la matriz de confusión y el tiempo de procesamiento."),
 head("4.1 Resultados en el conjunto de prueba interno"),
 body(f"Sobre las {it['images']} imágenes de prueba, el modelo alcanzó una exactitud de {f4(it['accuracy'])} y un F1 macro de {f4(it['f1_macro'])}. El minador, la roya y la hoja sana se reconocen con valores de F1 superiores a 0,93. La arañita roja es la clase más débil: de {ar['support']} imágenes, el modelo reconoce {round(ar['recall'] * ar['support'])}, y se confunde principalmente con la roya."),
 table(["Clase", "Precisión", "Sensibilidad", "F1", "Imágenes"], [[NOMBRE[c], f4(it["per_class"][c]["precision"]), f4(it["per_class"][c]["recall"]), f4(it["per_class"][c]["f1"]), it["per_class"][c]["support"]] for c in C], [2960, 1600, 1600, 1600, 1600]),
 caption("Métricas por clase en el conjunto de prueba interno."),
 figure(image(ROOT / "ml/outputs/final/confusion_matrix.png", "biocafe_matriz_confusion.png", 3474720)),
 caption("Matriz de confusión del modelo final en el conjunto de prueba interno."),
 head("4.2 Generalización a imágenes externas"),
 body("El conjunto externo permitió medir cómo se comporta el sistema con imágenes de otro origen. La primera versión del modelo, una MobileNetV2 de tres clases, obtenía 0,9561 de exactitud en su prueba interna pero solo 0,6137 en JMuBEN. Esa diferencia llevó a revisar los datos, a corregir el reparto, a incorporar BRACOL, a reforzar el aumento de datos y a cambiar de arquitectura. Con esos cambios, la exactitud en JMuBEN subió a 0,8003, y se mantuvo al añadir la cuarta clase."),
 table(["Versión del modelo", "Exactitud", "F1 macro (3 clases)", "Sens. minador", "Sens. roya", "Sens. sana"],
       [[n, f4(r["accuracy"]), f4(macro3(r)), f4(r["per_class"]["minador"]["recall"]), f4(r["per_class"]["roya"]["recall"]), f4(r["per_class"]["sana"]["recall"])] for n, r in (("v1: MobileNetV2, 3 clases", hold_v1), ("v2: EfficientNet-B0, 3 clases", hold_v2), ("v3: EfficientNet-B0, 4 clases", hold))],
       [2960, 1200, 1400, 1300, 1250, 1250]),
 caption(f"Resultados en el conjunto externo JMuBEN ({hold['images']} imágenes; no contiene arañita roja)."),
 body(f"La diferencia entre la exactitud interna ({f4(it['accuracy'])}) y la externa ({f4(hold['accuracy'])}) muestra que la prueba interna sobrestima el desempeño real, y que la cifra que mejor describe el sistema es la externa. En JMuBEN el modelo reconoce todas las hojas sanas, pero solo el {hold['per_class']['minador']['recall'] * 100:.0f} % de las hojas con minador, que confunde con frecuencia con la roya. Debe tenerse en cuenta que JMuBEN está formado por recortes de hojas ampliados con aumento de datos por sus autores, por lo que sus imágenes no son independientes entre sí, y que no se dispone de fotografías de campo tomadas en Colombia."),
 head("4.3 Análisis de la arañita roja"),
 body("La arañita roja solo está disponible en RoCoLe, con 152 imágenes tras la depuración. Se buscaron otros conjuntos públicos y los tres encontrados resultaron ser copias o versiones aumentadas de RoCoLe. Para evaluar esta clase con más imágenes que las 22 del conjunto de prueba se realizó una validación cruzada de tres particiones por grupos, en la que cada imagen se evalúa una sola vez, y se compararon cinco variantes de entrenamiento. Estos experimentos de exploración se ejecutaron en un equipo local con GPU NVIDIA; el modelo que se entrega es el entrenado en Google Colab."),
 table(["Variante", "Sensibilidad", "Precisión", "F1", "IC 95 % del F1", "Exactitud general"],
       [[n, f4(cv[k]["pooled"]["per_class"]["arana_roja"]["recall"]), f4(cv[k]["pooled"]["per_class"]["arana_roja"]["precision"]), f4(cv[k]["pooled"]["per_class"]["arana_roja"]["f1"]),
         f"{f3(cv[k]['pooled']['arana_roja_ci95']['f1'][0])} – {f3(cv[k]['pooled']['arana_roja_ci95']['f1'][1])}", f4(cv[k]["pooled"]["accuracy"])]
        for n, k in (("Receta base", "baseline_corrida1"), ("Recorte hacia la hoja", "leafcrop"), ("Pérdida focal y mayor peso", "boost"), ("Entrada de 320 píxeles", "res320"), ("Recorte y 320 píxeles", "leafcrop_res320"))],
       [2560, 1300, 1200, 1100, 1700, 1500]),
 caption("Validación cruzada de la arañita roja (152 imágenes evaluadas una vez por variante)."),
 body("Ninguna variante supera a la receta base: el F1 se mantiene entre 0,56 y 0,58 y los intervalos de confianza se solapan casi por completo. Las variantes solo desplazan el equilibrio entre sensibilidad y precisión. El error es siempre el mismo, la confusión entre arañita roja y roya, lo que indica que el límite está en los datos disponibles y no en el método de entrenamiento. Por ello se mantuvo la receta y se incorporó a la aplicación la regla de duda entre ambas clases."),
 body(f"En el conjunto de prueba interno, esa regla se activa en {duda['test']['doubt']} de las {duda['test']['images']} imágenes: evita {duda['test']['doubt_errors_avoided']} errores y deja como duda {duda['test']['doubt_correct_hidden']} respuestas que habrían sido correctas; en los {duda['test']['doubt_true_class_in_pair']} casos, la clase real es una de las dos que se muestran. La precisión de las respuestas afirmadas como arañita roja pasa de {f4(duda['test']['arana_roja_without_rule'][1])} a {f4(duda['test']['arana_roja_affirmed'][1])}, y la exactitud de lo que la aplicación afirma, de {f4(duda['test']['accuracy_all'])} a {f4(duda['test']['accuracy_affirmed'])}. La regla no mejora el modelo: evita que una parte de los casos dudosos se presente como una respuesta segura."),
 head("4.4 Tiempo de procesamiento y pruebas de funcionamiento"),
 body(f"En un teléfono de gama media (Motorola Edge 30, Android 14), la inferencia tarda una mediana de {phone['median_ms']:.0f} ms y un percentil 95 de {phone['p95_ms']:.0f} ms, medidos sobre 50 ejecuciones tras 5 de calentamiento. No se observaron diferencias entre usar dos y cuatro hilos de CPU, y las predicciones son idénticas en ambos casos. El archivo de instalación ocupa 47,5 MB, de los cuales 16,1 MB corresponden al modelo."),
 body(f"El funcionamiento se verificó con 16 pruebas unitarias y 10 pruebas instrumentadas ejecutadas en el teléfono. Estas últimas comprueban la paridad entre el modelo en Python y el modelo en el dispositivo en dos niveles: con el modelo aislado, la diferencia máxima de probabilidad fue inferior a 0,000001; con el flujo completo, que incluye la decodificación y el redimensionado de la imagen, la clase coincidió en las 10 imágenes de referencia. También se comprobó el manejo de archivos dañados, de imágenes de 12 megapíxeles y de la orientación de la fotografía."),
 head("4.5 Limitaciones de la evaluación"),
 body("No se realizó una evaluación con fotografías tomadas en fincas de Norte de Santander, por lo que el desempeño en las condiciones del departamento no está medido. El modelo solo conoce hojas: ante una imagen que no lo es, responde igualmente con alguna de las cuatro clases. RoCoLe contiene café Robusta de Ecuador, y BRACOL y parte de DECAFIA proceden de Brasil, mientras que en Colombia predomina el arábica. Además, cada configuración se entrenó una sola vez, por lo que no se cuantificó la variación entre entrenamientos del modelo final. El sistema es un prototipo académico de apoyo y no una herramienta de diagnóstico."),
]
# ---------------- Conclusiones
CONC = [
 body("Respecto al primer objetivo, la identificación de las plagas y enfermedades del café y de sus características visuales permitió delimitar el alcance del sistema. El análisis de viabilidad resultó decisivo: al restringir el trabajo a las afectaciones visibles en la hoja se descartaron la broca y las cochinillas, y se evitó construir un modelo sobre síntomas que una fotografía de la hoja no puede mostrar."),
 body("Respecto al segundo objetivo, la selección inicial de modelos y conjuntos de datos tuvo que corregirse con evidencia. MobileNet se había considerado la alternativa óptima por su ligereza, pero al medir ambas arquitecturas sobre una fuente no vista, EfficientNet-B0 generalizó mejor (F1 macro de 0,8494 frente a 0,7313). De igual forma, los conjuntos de datos seleccionados contenían duplicados, etiquetas contradictorias y categorías distintas de las esperadas, lo que muestra que un conjunto público debe auditarse antes de usarse."),
 body(f"Respecto al tercer objetivo, se construyó un sistema funcional que integra una red neuronal convolucional entrenada con aceleración CUDA y una aplicación móvil que la ejecuta sin conexión, con una latencia de {phone['median_ms']:.0f} ms en un teléfono de gama media. El procesamiento paralelo se limitó al que ofrecen los marcos de trabajo en la GPU y en la CPU del teléfono; no fue necesario recurrir a OpenMP ni a MPI, y la segmentación de lesiones no se implementó."),
 body(f"Respecto al cuarto objetivo, la evaluación mostró que una exactitud alta sobre los datos propios no garantiza un buen desempeño real. La primera versión del modelo obtenía 0,9561 en su prueba interna y 0,6137 en un conjunto externo; tras corregir el reparto de los datos, ampliar las fuentes, reforzar el aumento de datos y cambiar de arquitectura, la exactitud externa subió a {f4(hold['accuracy'])}. Persisten dos debilidades: la confusión entre minador y roya en imágenes nuevas y el bajo desempeño en arañita roja, que cinco variantes de entrenamiento no lograron mejorar por tratarse de una limitación de los datos disponibles."),
 body("En conjunto, el proyecto demuestra la viabilidad de llevar un modelo de aprendizaje profundo a un dispositivo móvil para apoyar la identificación de afectaciones en hojas de café, y a la vez deja claro que su fiabilidad depende de la calidad y variedad de los datos y de evaluarlo con imágenes distintas de las usadas para entrenar."),
 head("Recomendaciones"),
 body("Se recomienda, en primer lugar, recolectar fotografías propias en fincas de Norte de Santander, etiquetadas con apoyo de personal experto, tanto para entrenar como para evaluar el sistema en las condiciones reales del departamento; esto es indispensable para la arañita roja y para incorporar la mancha de hierro y el ojo de gallo. En segundo lugar, añadir una clase para imágenes que no corresponden a hojas, de modo que la aplicación pueda rechazarlas. En tercer lugar, repetir los entrenamientos con varias semillas para cuantificar la variación de los resultados. Finalmente, abordar la segmentación de las lesiones como un servicio en servidor, lo que permitiría estimar la severidad de la afectación, y mantener en la aplicación la advertencia de que se trata de una herramienta de apoyo que no sustituye el criterio de un especialista."),
]
REFS = [
 ref("[39] J. Parraga-Alava, K. Cusme, A. Loor, y E. Santander, «RoCoLe: A robusta coffee leaf images dataset», Mendeley Data, v2, 2019, doi: 10.17632/c5yvn32dzg.2."),
 ref("[40] L. E. Rosas Ruiz, A. F. Salom Medina, y J. G. Barrero Perez, «DECAFIA: A Field-Collected Coffee Leaf Disease Detection Dataset from Santander, Colombia (CoffeeLeaf-CO)», Zenodo, 2026, doi: 10.5281/zenodo.19931904."),
 ref("[41] R. A. Krohling, G. J. M. Esgario, y J. A. Ventura, «BRACOL - A Brazilian Arabica Coffee Leaf images dataset to identification and quantification of coffee diseases and pests», Mendeley Data, v1, 2019, doi: 10.17632/yy2k5y8mxg.1."),
 ref("[42] J. Jepkoech, B. Kenduiywo, D. Mugo, y E. Chebet, «JMuBEN», Mendeley Data, v1, 2021, doi: 10.17632/t2r6rszp5c.1."),
 ref("[43] J. Jepkoech, D. Mugo, B. Kenduiywo, y E. Chebet, «JMuBEN2», Mendeley Data, v1, 2021, doi: 10.17632/tgv3zb82nd.1."),
 ref("[44] M. Tan y Q. V. Le, «EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks», 2019, arXiv: arXiv:1905.11946."),
]
body_start = x.index("<w:body>"); ps = re.findall(r"<w:p[ >].*?</w:p>", x[body_start:], flags=re.S)
txt = lambda p: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
def find(prefix):
    m = [p for p in ps if txt(p).strip().startswith(prefix)]; assert len(m) == 1, (prefix, len(m)); return m[0]
t365, t366, t369, r38 = find("Expresa de manera puntual"), find("Exposición del alcance objetivo específico 1"), find("Exponga las opiniones personales"), find("[38]")
for old, new in ((t365, "".join(P)), (t366, ""), (t369, "".join(CONC)), (r38, r38 + "".join(REFS))):
    assert x.count(old) == 1; x = x.replace(old, new)
doc_path.write_text(x, encoding="utf8")
rels_path.write_text(rels.replace("</Relationships>", "".join(new_rels) + "</Relationships>"), encoding="utf8")
print("parrafos nuevos:", len(P) + len(CONC) + len(REFS), "| imagenes:", len(new_rels))
