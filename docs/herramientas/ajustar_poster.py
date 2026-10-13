"""Updates the poster (.pptx) with the results of objectives 3 and 4 from the completed report.

Usage: python ajustar_poster.py <unpacked pptx dir> <repo root>
Edits ppt/slides/slide1.xml in place: texts, positions, three app screenshots and three stat cards.
"""
import re, shutil, struct, sys, zipfile
from pathlib import Path
from xml.sax.saxutils import escape

UN, ROOT = Path(sys.argv[1]), Path(sys.argv[2])
slide = UN / "ppt/slides/slide1.xml"; x = slide.read_text(encoding="utf8")
CM = 360000
SHAPE = r"<p:(sp|pic|graphicFrame)>.*?</p:\1>"

def shape(name):
    for m in re.finditer(SHAPE, x, flags=re.S):
        if f'name="{name}"' in m.group(0): return m.group(0)
    raise KeyError(name)

def put(old, new):
    global x
    assert x.count(old) == 1; x = x.replace(old, new)

def move(name, y=None, h=None, x_cm=None, w=None):
    sp = shape(name); m = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"\s*/>\s*<a:ext cx="(\d+)" cy="(\d+)"\s*/>', sp)
    ox, oy, cx, cy = map(int, m.groups())
    new = f'<a:off x="{int(x_cm * CM) if x_cm is not None else ox}" y="{int(y * CM) if y is not None else oy}" /><a:ext cx="{int(w * CM) if w is not None else cx}" cy="{int(h * CM) if h is not None else cy}" />'
    put(sp, sp.replace(m.group(0), new, 1))

def set_paragraphs(name, paragraphs, keep=0):
    """Replace the paragraphs of a shape after the first `keep` ones."""
    sp = shape(name); ps = re.findall(r"<a:p>.*?</a:p>", sp, flags=re.S)
    start = sp.index(ps[keep]) if keep < len(ps) else sp.index("</p:txBody>")
    put(sp, sp[:start] + "".join(paragraphs) + sp[sp.index("</p:txBody>"):])

def run(text, size, bold=False, color=None):
    fill = f'<a:solidFill><a:schemeClr val="{color}" /></a:solidFill>' if color else ""
    return f'<a:r><a:rPr lang="es-CO" sz="{size}"{" b=\"1\"" if bold else ""} dirty="0">{fill}</a:rPr><a:t>{escape(text)}</a:t></a:r>'

def card_body(*runs):
    return ('<a:p><a:pPr algn="l"><a:spcBef><a:spcPts val="0" /></a:spcBef><a:spcAft><a:spcPts val="0" /></a:spcAft><a:buNone /></a:pPr>' + "".join(runs) + "</a:p>")

def bullet(text, size=2800):
    return ('<a:p><a:pPr marL="571500" indent="-571500"><a:spcBef><a:spcPts val="0" /></a:spcBef><a:spcAft><a:spcPts val="600" /></a:spcAft>'
            '<a:buFont typeface="Arial" /><a:buChar char="•" /></a:pPr>' + run(text, size) + "</a:p>")

# ---- left column: abstract now reports what was built
old = ("Se aplicará la metodología CRISP-DM y los datos se obtendrán de repositorios especializados. En este avance se presentan la identificación de las afectaciones y la selección de modelos, datasets y herramientas de paralelización. "
       "El producto esperado es un prototipo de software capaz de analizar imágenes y reconocer posibles plagas o enfermedades.")
put(old, "Se aplicó la metodología CRISP-DM con imágenes de repositorios públicos. Se construyó BioCafe, una aplicación móvil que clasifica una hoja de café en sana, roya, minador o arañita roja sin conexión a internet, "
         "y se evaluó con imágenes internas y externas: 0,94 y 0,81 de exactitud, respectivamente.")

put("<a:t> CNN de clasificación y segmentación, con paralelización mediante CUDA.</a:t>", "<a:t> CNN de clasificación entrenada en GPU mediante CUDA.</a:t>")

# ---- right column: compact the viability table and the objective 2 cards
table = shape("Tabla viabilidad"); put(table, table.replace('<a:tr h="804672">', '<a:tr h="504000">'))
move("Tabla viabilidad", h=14.0)
move("Objetivo 2", y=39.0)
for name, cx, cy in (("Tarjeta Clasificación", 41.1, 42.6), ("Tarjeta Segmentación", 59.4, 42.6), ("Tarjeta Datasets", 41.1, 50.0), ("Tarjeta Paralelismo", 59.4, 50.0)):
    move(name, y=cy, h=6.9)
T = "tx1"
set_paragraphs("Tarjeta Clasificación", [card_body(run("EfficientNet-B0", 2800, True, T), run(": superó a MobileNetV2 en una fuente no vista (F1 macro 0,85 frente a 0,73).", 2800, False, T))], keep=1)
set_paragraphs("Tarjeta Segmentación", [card_body(run("Mask R-CNN", 2800, True, T), run(": analizada para delimitar lesiones. No se implementó; queda como trabajo futuro.", 2800, False, T))], keep=1)
set_paragraphs("Tarjeta Datasets", [card_body(run("RoCoLe, DECAFIA y BRACOL", 2800, True, T), run(": 3736 imágenes sin duplicados. JMuBEN quedó como prueba externa.", 2800, False, T))], keep=1)
set_paragraphs("Tarjeta Paralelismo", [card_body(run("NVIDIA CUDA", 2800, True, T), run(" en Google Colab (GPU T4) para entrenar; ", 2800, False, T), run("TensorFlow Lite", 2800, True, T), run(" con varios hilos de CPU en el teléfono.", 2800, False, T))], keep=1)

move("Titulo flujo", y=57.4)
put("<a:t>Flujo propuesto del sistema</a:t>", "<a:t>Flujo del sistema</a:t>")
put("<a:t>Modelo MobileNet</a:t>", "<a:t>Modelo EfficientNet-B0</a:t>")
for i in (1, 2, 3, 4): move(f"Paso {i}", y=59.1, h=4.6)
for i in (1, 2, 3): move(f"Flecha {i}", y=60.75)

# ---- new block: objectives 3 and 4
title34 = shape("Objetivo 2")
new_title = (title34.replace('id="1030" name="Objetivo 2"', 'id="1050" name="Objetivos 3 y 4"')
             .replace("<a:t>Objetivo 2.</a:t>", "<a:t>Objetivos 3 y 4.</a:t>")
             .replace("<a:t> Selección para una aplicación móvil, considerando precisión, tiempo de procesamiento, tamaño y consumo de recursos:</a:t>",
                      "<a:t> Se construyó BioCafe (Kotlin, modelo dentro del teléfono) y se evaluó con imágenes internas y externas:</a:t>"))
new_title = re.sub(r'<a:off x="(\d+)" y="\d+"', lambda m: f'<a:off x="{m.group(1)}" y="{int(64.4 * CM)}"', new_title, count=1)

rels_path = UN / "ppt/slides/_rels/slide1.xml.rels"; rels = rels_path.read_text(encoding="utf8")
informe = zipfile.ZipFile(ROOT / "docs/Informe_BioCafe_completado.docx")
pics, new_rels = [], []
TOP, HEIGHT = 67.6, 12.6
for k, name in enumerate(("biocafe_inicio.png", "biocafe_resultado.png", "biocafe_duda.png")):
    data = informe.read(f"word/media/{name}"); (UN / "ppt/media" / name).write_bytes(data)
    w, h = struct.unpack(">II", data[16:24]); width = HEIGHT * w / h
    rid = f"rId{10 + k}"; new_rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{name}" />')
    left = 41.1 + k * (width + 0.45)
    pics.append(f'<p:pic><p:nvPicPr><p:cNvPr id="{1051 + k}" name="Captura BioCafe {k + 1}" descr="Captura de pantalla de la aplicación BioCafe" /><p:cNvPicPr><a:picLocks noChangeAspect="1" /></p:cNvPicPr><p:nvPr /></p:nvPicPr>'
                f'<p:blipFill><a:blip r:embed="{rid}" /><a:stretch><a:fillRect /></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{int(left * CM)}" y="{int(TOP * CM)}" /><a:ext cx="{int(width * CM)}" cy="{int(HEIGHT * CM)}" /></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst /></a:prstGeom><a:ln w="12700"><a:solidFill><a:schemeClr val="bg1"><a:lumMod val="75000" /></a:schemeClr></a:solidFill></a:ln></p:spPr></p:pic>')
right_edge = 41.1 + 3 * width + 2 * 0.45
card = shape("Tarjeta Clasificación"); stats = []
STAT_X = right_edge + 0.7; STAT_W = 76.7 - STAT_X
for k, (number, label) in enumerate((("94 %", "exactitud en la prueba interna"), ("81 %", "exactitud en un conjunto externo"), ("48 ms", "por imagen en un teléfono"))):
    sp = card.replace('id="1031" name="Tarjeta Clasificación"', f'id="{1060 + k}" name="Cifra {k + 1}"').replace('anchor="t"', 'anchor="ctr"')
    sp = re.sub(r'<a:off x="\d+" y="\d+"\s*/>\s*<a:ext cx="\d+" cy="\d+"\s*/>', f'<a:off x="{int(STAT_X * CM)}" y="{int((TOP + k * 4.3) * CM)}" /><a:ext cx="{int(STAT_W * CM)}" cy="{int(4.0 * CM)}" />', sp, count=1)
    body = ('<a:p><a:pPr algn="ctr"><a:spcBef><a:spcPts val="0" /></a:spcBef><a:spcAft><a:spcPts val="0" /></a:spcAft><a:buNone /></a:pPr>'
            f'<a:r><a:rPr lang="es-CO" sz="5400" b="1" dirty="0"><a:solidFill><a:schemeClr val="accent2"><a:lumMod val="75000" /></a:schemeClr></a:solidFill></a:rPr><a:t>{number}</a:t></a:r></a:p>'
            '<a:p><a:pPr algn="ctr"><a:spcBef><a:spcPts val="0" /></a:spcBef><a:spcAft><a:spcPts val="0" /></a:spcAft><a:buNone /></a:pPr>' + run(label, 2400, False, T) + "</a:p>")
    ps = re.findall(r"<a:p>.*?</a:p>", sp, flags=re.S); sp = sp[:sp.index(ps[0])] + body + sp[sp.index("</p:txBody>"):]
    stats.append(sp)
conclusions = shape("Conclusiones")
put(conclusions, new_title + "".join(pics) + "".join(stats) + conclusions)
rels_path.write_text(rels.replace("</Relationships>", "".join(new_rels) + "</Relationships>"), encoding="utf8")

# ---- conclusions and references
move("Conclusiones", y=81.3, h=17.2)
set_paragraphs("Conclusiones", [
    bullet("Se construyó BioCafe, una aplicación Android que clasifica hojas de café en sana, roya, minador o arañita roja dentro del teléfono, sin internet y en 48 ms."),
    bullet("EfficientNet-B0 generalizó mejor que MobileNet. La exactitud fue de 0,94 en la prueba interna y de 0,81 en un conjunto externo; la externa es la que describe el uso real."),
    bullet("Debilidades: confunde minador con roya en imágenes nuevas, y la arañita roja, con una sola fuente de 152 imágenes, alcanza un F1 de 0,57 que cinco variantes de entrenamiento no mejoraron."),
    bullet("Trabajo futuro: fotografías de fincas de Norte de Santander, una clase para imágenes que no son hojas y la segmentación de lesiones."),
], keep=1)
move("Referencias", y=99.3, h=17.6)
refs = shape("Referencias"); ps = re.findall(r"<a:p>.*?</a:p>", refs, flags=re.S)
def ref_like(model, text):
    first = re.search(r"<a:r>.*?</a:r>", model, flags=re.S).group(0); rpr = re.search(r"<a:rPr[^>]*?(?:/>|>.*?</a:rPr>)", first, flags=re.S).group(0)
    return model[:model.index("<a:r>")] + f"<a:r>{rpr}<a:t>{escape(text)}</a:t></a:r></a:p>"
def after(prefix, text):
    global refs
    p = next(q for q in ps if "".join(re.findall(r"<a:t>([^<]*)</a:t>", q)).startswith(prefix)); refs_new = refs.replace(p, p + ref_like(p, text)); return refs_new
old_refs = refs
refs = after("Invesa", "Krohling, R. A., Esgario, G. J. M. y Ventura, J. A. (2019). BRACOL: A Brazilian Arabica Coffee Leaf images dataset. Mendeley Data, v1. doi: 10.17632/yy2k5y8mxg.1")
refs = after("NVIDIA", "Parraga-Alava, J., Cusme, K., Loor, A. y Santander, E. (2019). RoCoLe: A robusta coffee leaf images dataset. Mendeley Data, v2. doi: 10.17632/c5yvn32dzg.2")
refs = after("Sandler", "Tan, M. y Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. arXiv:1905.11946.")
put(old_refs, refs)
slide.write_text(x, encoding="utf8")
print("poster actualizado")
