"""Build the three Word deliverables of the review from datos/ and contenido.py.

Usage: python generar_documentos.py <solucion dir>
Writes:
  Articulo_IEEE_Revision_MPI_BioCafe.docx   (IEEE two-column short article)
  Trazabilidad_Revision_MPI_BioCafe.docx    (constructs, prompts, abstracts, comparative table, evaluation)
  Semilla_Zotero_Referencias.docx           (Word copy of the Zotero seed)
  figuras/flujo_seleccion.png
"""
import json, re, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "herramientas"))
import contenido as C
from claves import key

DATA = ROOT / "datos"
REFS = json.load(open(DATA / "referencias.json", encoding="utf8"))
CONS = json.load(open(DATA / "constructos.json", encoding="utf8"))
BUSQ = json.load(open(DATA / "busqueda_crossref.json", encoding="utf8"))
CRIB = json.load(open(DATA / "cribado.json", encoding="utf8"))
BY_KEY = {key(r): r for r in REFS}
CONS_BY_ID = {c["id"]: c for c in CONS}
FONT = "Times New Roman"
CITE = re.compile(r"\[(@[^\]]+)\]")
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

# ---------------------------------------------------------------- citation order
HALLAZGOS = [
    ("castello2023analyzing", "Elegir biblioteca MPI y algoritmo de Allreduce acelera el entrenamiento de CNN de 1,2 a 2,8 veces"),
    ("nuriyev2024suara", "SUARA más que duplica la velocidad del Allreduce de Open MPI y mejora 9 % el entrenamiento de ResNet-50"),
    ("thune2023detailed", "Modelo de comunicación punto a punto con 84 % de precisión para 8192 procesos"),
    ("patil2023study", "Paralelismo de modelo: aceleración de 1,38 veces y 62,13 % frente a 55,72 % de exactitud"),
    ("maruf2024optimizing", "Paralelismo en tubería, de datos y de modelo: 44,87 % menos tiempo de entrenamiento"),
    ("pekkila2022scalable", "MPI compatible con CUDA: 50 % a 87 % de la eficiencia esperada con hasta 64 GPU"),
    ("chavarro2023influence", "Roya del café: la arquitectura base cambia el resultado hasta en 70 %"),
    ("araaf2024coffee", "Roya del café con YOLOv8 en un dispositivo de borde: mAP de 73,2 %"),
    ("soares2022early", "Roya presintomática a los 15 días con imágenes multiespectrales: 80 % de exactitud"),
    ("duhan2025lite", "Modelo ligero en Raspberry Pi: 90,84 % de exactitud en café"),
    ("adelaja2025leveraging", "CoffNet: 97,88 % de exactitud a 125,93 imágenes por segundo"),
]

def citation_order():
    order = []
    def scan(text):
        for group in CITE.findall(text):
            for k in re.findall(r"@([\w-]+)", group):
                if k not in order: order.append(k)
    for _, blocks in C.SECCIONES:
        for b in blocks:
            if isinstance(b, str): scan(b)
            elif b == ("tabla", "hallazgos"):
                for k, _ in HALLAZGOS: scan(f"[@{k}]")
    missing = set(BY_KEY) - set(order)
    unknown = set(order) - set(BY_KEY)
    assert not missing and not unknown, (missing, unknown)
    return {k: i + 1 for i, k in enumerate(order)}

NUM = citation_order()
ORDERED = sorted(BY_KEY, key=NUM.get)

def cite_text(text):
    def rep(m):
        nums = sorted(NUM[k] for k in re.findall(r"@([\w-]+)", m.group(1)))
        return "[" + "], [".join(map(str, nums)) + "]"
    return CITE.sub(rep, text)

# ---------------------------------------------------------------- IEEE reference text
def ieee_authors(r):
    def short(a):
        given = re.split(r"[\s]+", a["given"].replace(".", ". ").strip())
        initials = " ".join(("-".join(p[0] + "." for p in g.split("-") if p) if not g.endswith(".") else g) for g in given if g)
        return f"{initials} {a['family']}".strip()
    names = [short(a) for a in r["autores"]]
    if len(names) > 6: return names[0] + " et al."
    return names[0] if len(names) == 1 else (", ".join(names[:-1]) + (", and " if len(names) > 2 else " and ") + names[-1])

def ieee_parts(r):
    loc = [f"vol. {r['volumen']}"] if r["volumen"] else []
    if r["numero"]: loc.append(f"no. {r['numero']}")
    if r["paginas"]: loc.append(("pp. " + r["paginas"].replace("-", "–")) if "-" in r["paginas"] else f"p. {r['paginas']}")
    elif r["articulo"]: loc.append(f"Art. no. {r['articulo']}")
    loc.append(str(r["anio"]))
    return f"{ieee_authors(r)}, “{r['titulo']},” ", r["revista"], ", " + ", ".join(loc) + ", doi: "

# ---------------------------------------------------------------- docx helpers
def set_font(run, size=None, bold=None, italic=None, small_caps=None, color=None, keep=None):
    run.font.name = FONT
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONT)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic
    if small_caps is not None: run.font.small_caps = small_caps
    if color: run.font.color.rgb = color

def para(doc_or_cell, text="", size=10, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=None, before=0, after=0, **fmt):
    p = doc_or_cell.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.0
    if indent is not None: pf.first_line_indent = Inches(indent)
    if text: set_font(p.add_run(text), size, **fmt)
    if fmt.get("keep"): pf.keep_with_next = True
    return p

def add_hyperlink(p, url, text, size):
    r_id = p.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    run = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    for tag, val in (("w:rFonts", None), ("w:color", "1F4E99"), ("w:u", "single"), ("w:sz", str(int(size * 2)))):
        e = OxmlElement(tag)
        if tag == "w:rFonts":
            for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): e.set(qn(a), FONT)
        else: e.set(qn("w:val"), val)
        rpr.append(e)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve")
    run.append(rpr); run.append(t); h.append(run); p._p.append(h)

def set_columns(section, num, space=0.25):
    cols = section._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols"); section._sectPr.append(cols)
    cols.set(qn("w:num"), str(num)); cols.set(qn("w:space"), str(int(space * 1440)))

def page_setup(section, top=0.75, bottom=1.0, side=0.625, landscape=False):
    section.page_width, section.page_height = (Inches(11), Inches(8.5)) if landscape else (Inches(8.5), Inches(11))
    section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    section.top_margin, section.bottom_margin = Inches(top), Inches(bottom)
    section.left_margin = section.right_margin = Inches(side)

def cell_shade(cell, hex_color):
    tcpr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_color); tcpr.append(shd)

def table(doc, header, rows, widths, size=8, header_fill="D9E2F3"):
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = OxmlElement("w:tblHeader"); hdr.set(qn("w:val"), "true"); t.rows[0]._tr.get_or_add_trPr().append(hdr)
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; cell_shade(c, header_fill)
        set_font(c.paragraphs[0].add_run(h), size, bold=True); c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            p = cells[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if isinstance(v, tuple) and v[0] == "link": add_hyperlink(p, v[1], v[2], size)
            else: set_font(p.add_run(str(v)), size)
    layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(layout)
    for i, w in enumerate(widths): t.columns[i].width = Inches(w)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    return t

def no_split_rows(t):
    for row in t.rows:
        trpr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trpr.append(cs)

def short_name(r):
    fam = r["autores"][0]["family"]
    return f"{fam} et al. ({r['anio']})" if len(r["autores"]) > 2 else (f"{fam} y {r['autores'][1]['family']} ({r['anio']})" if len(r["autores"]) == 2 else f"{fam} ({r['anio']})")

# ---------------------------------------------------------------- figure
def flujo_figure(path):
    uniq = len({x["doi"] for s in BUSQ["busquedas"] for x in s["candidatos"]})
    listed = sum(len(s["candidatos"]) for s in BUSQ["busquedas"])
    alt = json.load(open(DATA / "alternativas_verificadas.json", encoding="utf8"))
    r1 = sum(len(v) for v in json.load(open(DATA / "seleccion_ronda1.json", encoding="utf8")).values())
    assessed = r1 + len(alt) + len(CRIB["ronda3"]["incluidos"])
    no_abs = len(CRIB["ronda1"]["excluidos_sin_resumen"]) + sum(1 for r in alt if not r["resumen"])
    red = len(CRIB["ronda2"]["no_elegidos_con_resumen"])
    assert assessed - no_abs - red == len(REFS)
    seen = {x["doi"] for s in BUSQ["busquedas"] for x in s["candidatos"]}
    pre = [d for v in json.load(open(DATA / "seleccion_ronda1.json", encoding="utf8")).values() for d in v] + [r["doi"] for r in alt] + CRIB["ronda3"]["incluidos"]
    assert len(set(pre)) == assessed and set(pre) <= seen, set(pre) - seen
    fig, ax = plt.subplots(figsize=(3.6, 3.3), dpi=300); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 10)
    main = [(9.0, f"{len(BUSQ['busquedas'])} búsquedas en Crossref\n{listed} registros revisados"),
            (6.8, f"{uniq} registros únicos"), (4.6, f"{assessed} preseleccionados\n(DOI verificado)"), (2.0, f"{len(REFS)} artículos incluidos")]
    for y, txt in main:
        ax.text(3.2, y, txt, ha="center", va="center", fontsize=6.5, family="serif",
                bbox=dict(boxstyle="round,pad=0.35", fc="#EEF3FA", ec="#1F4E99", lw=0.7))
    for (y1, _), (y2, _) in zip(main, main[1:]):
        ax.annotate("", xy=(3.2, y2 + 0.75), xytext=(3.2, y1 - 0.75), arrowprops=dict(arrowstyle="->", lw=0.7))
    side = [(5.75, f"Excluidos por título,\nruido o año: {uniq - assessed}"),
            (3.35, f"Sin resumen recuperable: {no_abs}\nRedundancia o alcance: {red}")]
    for y, txt in side:
        ax.text(9.6, y, txt, ha="center", va="center", fontsize=6, family="serif",
                bbox=dict(boxstyle="round,pad=0.3", fc="#FFF4E5", ec="#B26B00", lw=0.6))
        ax.annotate("", xy=(7.2, y), xytext=(3.2, y), arrowprops=dict(arrowstyle="->", lw=0.6))
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return {"listed": listed, "uniq": uniq, "assessed": assessed, "no_abs": no_abs, "red": red}

# ---------------------------------------------------------------- article
def build_article(out, fig_path):
    doc = Document(); s0 = doc.sections[0]; page_setup(s0)
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
    para(doc, C.TITULO, 22, WD_ALIGN_PARAGRAPH.CENTER, after=10)
    for name in C.AUTORES:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, after=0); set_font(p.add_run(name), 11)
        set_font(p.add_run(f"  ·  Identificación {C.IDENTIFICACION[name]}"), 9)
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, after=2); add_hyperlink(p, "mailto:" + C.CORREO[name], C.CORREO[name], 9)
    para(doc, "", after=2)
    for line in C.AFILIACION: para(doc, line, 10, WD_ALIGN_PARAGRAPH.CENTER, italic=True)
    para(doc, "", after=6)
    body = doc.add_section(WD_SECTION.CONTINUOUS); page_setup(body); set_columns(body, 2)

    def labeled(label, text):
        p = para(doc, after=4); set_font(p.add_run(label), 9, bold=True, italic=True); set_font(p.add_run(text), 9, bold=True)
    labeled("Resumen—", C.RESUMEN)
    labeled("Palabras clave—", C.PALABRAS_CLAVE)
    labeled("Abstract—", C.ABSTRACT)
    labeled("Index Terms—", C.INDEX_TERMS)

    tables = {"constructos": 0, "hallazgos": 0}; tcount = 0
    for si, (title, blocks) in enumerate(C.SECCIONES):
        para(doc, f"{ROMAN[si]}. {title}", 10, WD_ALIGN_PARAGRAPH.CENTER, before=8, after=4, small_caps=True, keep=True)
        for b in blocks:
            if isinstance(b, str):
                para(doc, cite_text(b), 10, indent=0.15)
            elif b[0] == "sub":
                para(doc, b[1], 10, WD_ALIGN_PARAGRAPH.LEFT, before=4, after=2, italic=True, keep=True)
            elif b[0] == "tabla":
                tcount += 1
                para(doc, f"Tabla {ROMAN[tcount - 1]}", 8, WD_ALIGN_PARAGRAPH.CENTER, before=6, small_caps=True)
                if b[1] == "constructos":
                    para(doc, "Constructos de la revisión y artículos incluidos", 8, WD_ALIGN_PARAGRAPH.CENTER, after=3, small_caps=True)
                    rows = []
                    for c in CONS:
                        nums = sorted(NUM[k] for k, r in BY_KEY.items() if r["constructo"] == c["id"])
                        area = "PyD" if c["area"].startswith("Computación") and "+" not in c["area"] else ("SI" if c["area"].startswith("Sistemas") and "+" not in c["area"] else "PyD + SI")
                        rows.append((c["id"], c["nombre"], area, ", ".join(f"[{n}]" for n in nums)))
                    t = table(doc, ["ID", "Constructo", "Área", "Referencias"], rows, [0.3, 1.75, 0.5, 0.75], 7)
                    para(doc, "PyD: Computación Paralela y Distribuida. SI: Sistemas Inteligentes.", 7, WD_ALIGN_PARAGRAPH.LEFT, before=2, after=6)
                else:
                    para(doc, "Hallazgos cuantitativos relevantes para BioCafe", 8, WD_ALIGN_PARAGRAPH.CENTER, after=3, small_caps=True)
                    t = table(doc, ["Ref.", "Hallazgo reportado en el resumen"], [(f"[{NUM[k]}]", txt) for k, txt in HALLAZGOS], [0.4, 2.9], 7)
                    para(doc, "", after=6)
                no_split_rows(t)
            elif b[0] == "figura":
                p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=6); p.add_run().add_picture(str(fig_path), width=Inches(3.2))
                para(doc, "Fig. 1. Flujo de identificación y selección de los estudios.", 8, WD_ALIGN_PARAGRAPH.CENTER, after=6)
    para(doc, "Referencias", 10, WD_ALIGN_PARAGRAPH.CENTER, before=8, after=4, small_caps=True, keep=True)
    for k in ORDERED:
        r = BY_KEY[k]; a, journal, tail = ieee_parts(r)
        p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, after=1)
        p.paragraph_format.left_indent = Inches(0.3); p.paragraph_format.first_line_indent = Inches(-0.3)
        set_font(p.add_run(f"[{NUM[k]}]\t{a}"), 8); set_font(p.add_run(journal), 8, italic=True); set_font(p.add_run(tail), 8)
        add_hyperlink(p, r["url"], r["doi"], 8); set_font(p.add_run("."), 8)
    doc.save(out)

# ---------------------------------------------------------------- traceability
def heading(doc, text, level=1):
    size = {1: 14, 2: 12}[level]
    return para(doc, text, size, WD_ALIGN_PARAGRAPH.LEFT, before=12 if level == 1 else 8, after=4, bold=True, color=RGBColor(0x1F, 0x3A, 0x5F), keep=True)

def ref_line(doc, r, size=10, prefix=None):
    a, journal, tail = ieee_parts(r)
    p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
    set_font(p.add_run(prefix or f"[{NUM[key(r)]}] "), size, bold=True)
    set_font(p.add_run(a), size); set_font(p.add_run(journal), size, italic=True); set_font(p.add_run(tail), size)
    add_hyperlink(p, r["url"], r["url"], size); return p

def build_traceability(out, flow):
    doc = Document(); s = doc.sections[0]; page_setup(s, 1, 1, 1)
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(11)
    para(doc, "Documento de trazabilidad de la revisión sistemática", 18, WD_ALIGN_PARAGRAPH.CENTER, before=60, after=8, bold=True)
    para(doc, C.TITULO, 13, WD_ALIGN_PARAGRAPH.CENTER, after=16, italic=True)
    para(doc, "Proyecto: Sistema de detección temprana de plagas y enfermedades en cultivos de café (prototipo BioCafe)", 11, WD_ALIGN_PARAGRAPH.CENTER, after=4)
    para(doc, "Autoras:", 11, WD_ALIGN_PARAGRAPH.CENTER, after=0, bold=True)
    for line in C.autores_con_id(): para(doc, line, 11, WD_ALIGN_PARAGRAPH.CENTER, after=0)
    para(doc, "", after=4)
    for line in C.AFILIACION: para(doc, line, 11, WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "Cursos: Fundamentos de Computación Paralela y Distribuida · Sistemas Inteligentes", 11, WD_ALIGN_PARAGRAPH.CENTER, before=8)
    para(doc, f"Fecha de la búsqueda: {BUSQ['fecha']}", 11, WD_ALIGN_PARAGRAPH.CENTER, before=4)
    para(doc, "Este documento registra, en orden, cómo se construyó la revisión: de los constructos a los prompts, de los prompts a las "
         "búsquedas, de las búsquedas a las referencias, y de las referencias a su relación con el proyecto. Termina con la evaluación "
         "de la revisión y los ajustes que se le hicieron. La numeración [n] de las referencias es la misma del artículo IEEE.",
         11, before=24)
    doc.add_page_break()

    heading(doc, "1. Datos de la revisión")
    table(doc, ["Campo", "Valor"], [
        ("Título", C.TITULO), ("Title", C.TITLE_EN), ("Tipo", "Revisión sistemática descriptiva (artículo corto, máximo 10 páginas, formato IEEE)"),
        ("Autoras", "; ".join(C.autores_con_id())), ("Afiliación", " ".join(C.AFILIACION)),
        ("Base consultada", BUSQ["base"]), ("Periodo", "Artículos de revista publicados desde el 1 de enero de 2022"),
        ("Búsquedas", f"{len(BUSQ['busquedas'])} (8 constructos, cada cadena con y sin el filtro de ScienceDirect)"),
        ("Referencias incluidas", f"{len(REFS)} ({sum(r['doi'].startswith('10.1016/') for r in REFS)} de ScienceDirect), todas con DOI verificado"),
        ("Gestor de referencias", "Zotero, colección «BioCafe - Revisión sistemática MPI», cargada con el MCP de Zotero"),
    ], [1.6, 4.9], 10)

    heading(doc, "2. Resumen y abstract")
    heading(doc, "Resumen", 2); para(doc, C.RESUMEN, 11)
    p = para(doc, before=4); set_font(p.add_run("Palabras clave: "), 11, bold=True); set_font(p.add_run(C.PALABRAS_CLAVE), 11)
    heading(doc, "Abstract", 2); para(doc, C.ABSTRACT, 11)
    p = para(doc, before=4); set_font(p.add_run("Index terms: "), 11, bold=True); set_font(p.add_run(C.INDEX_TERMS), 11)

    heading(doc, "3. Constructos")
    para(doc, "Los constructos cruzan las unidades del curso de MPI (fundamentación, instalación en LAN y en clúster, comunicación punto "
         "a punto y colectiva) con los componentes inteligentes de BioCafe.", 11, after=6)
    table(doc, ["ID", "Constructo", "Área", "Definición operativa", "Indicadores"],
          [(c["id"], c["nombre"], c["area"], c["definicion"], c["indicadores"]) for c in CONS], [0.4, 1.3, 1.1, 2.2, 1.5], 9)

    heading(doc, "4. Prompts y estrategia de búsqueda")
    para(doc, "Cada prompt nace de un constructo y se tradujo a cadenas de búsqueda en inglés. Cada cadena se ejecutó dos veces: limitada a "
         "ScienceDirect (prefijo DOI 10.1016) y sin límite de editorial, con los filtros de artículo de revista y fecha desde 2022. "
         "El detalle completo está en 01_Constructos_y_prompts.md.", 11, after=6)
    rows = []
    for c in CONS:
        strings = []
        for q in c["consultas"]:
            tot = {s["filtro"].split(" ")[0]: s["resultados_totales"] for s in BUSQ["busquedas"] if s["consulta"] == q}
            strings.append(f"«{q}» (ScienceDirect: {tot['ScienceDirect']:,}; todas: {tot['todas']:,})".replace(",", "."))
        rows.append((c["id"], c["prompt"], "\n".join(strings)))
    table(doc, ["ID", "Prompt", "Cadenas de búsqueda (resultados totales)"], rows, [0.4, 3.3, 2.8], 9)

    heading(doc, "5. Criterios y flujo de selección")
    for label, text in (("Inclusión: ", "artículo de revista publicado desde 2022; DOI que resuelve en Crossref; resumen recuperable; relación directa con un constructo; preferencia por ScienceDirect."),
                        ("Exclusión: ", "ruido semántico de la búsqueda; fecha fuera del periodo; sin resumen recuperable; redundancia con otro trabajo incluido; fuera del alcance; presencia previa en la biblioteca de Zotero de las autoras.")):
        p = para(doc, after=3); set_font(p.add_run(label), 11, bold=True); set_font(p.add_run(text), 11)
    table(doc, ["Etapa", "Registros"], [
        ("Búsquedas ejecutadas", len(BUSQ["busquedas"])), ("Registros revisados (8 por búsqueda)", flow["listed"]),
        ("Registros únicos", flow["uniq"]), ("Preseleccionados con DOI verificado", flow["assessed"]),
        ("Excluidos por no tener resumen recuperable", flow["no_abs"]), ("Excluidos por redundancia o alcance", flow["red"]),
        ("Incluidos", len(REFS))], [4.5, 1.2], 10)
    para(doc, "Excluidos por redundancia o alcance:", 11, before=6, after=3, bold=True)
    table(doc, ["DOI", "Motivo"], [(("link", "https://doi.org/" + k, k), v) for k, v in CRIB["ronda2"]["no_elegidos_con_resumen"].items()], [2.3, 4.2], 9)

    heading(doc, "6. Fichas de las referencias: resumen y abstract")
    para(doc, "Para cada referencia se presenta la cita IEEE con su enlace DOI, el constructo, un resumen en español elaborado por las "
         "autoras y el abstract original tal como lo publica la fuente indicada.", 11, after=6)
    for k in ORDERED:
        r = BY_KEY[k]
        ref_line(doc, r, 10)
        p = para(doc, after=2); set_font(p.add_run("Constructo: "), 10, bold=True); set_font(p.add_run(f"{r['constructo']} {CONS_BY_ID[r['constructo']]['nombre']}"), 10)
        p = para(doc, after=2); set_font(p.add_run("Resumen: "), 10, bold=True); set_font(p.add_run(C.RESUMEN_ES[k]), 10)
        p = para(doc, after=10); set_font(p.add_run(f"Abstract ({r['fuente_resumen']}): "), 10, bold=True); set_font(p.add_run(r["resumen"]), 9, italic=True)

    heading(doc, "7. Relación de los resúmenes con el proyecto (en grupos)")
    para(doc, "Los resúmenes se agrupan de dos o tres según el aspecto del proyecto al que benefician.", 11, after=6)
    for gi, (title, keys, text) in enumerate(C.GRUPOS, 1):
        heading(doc, f"Grupo {gi}. {title}", 2)
        para(doc, "Referencias: " + "; ".join(f"[{NUM[k]}] {short_name(BY_KEY[k])}" for k in keys), 10, italic=True, after=3)
        para(doc, text, 11, after=6)

    comp = doc.add_section(WD_SECTION.NEW_PAGE); page_setup(comp, 0.8, 0.8, 0.7, landscape=True)
    heading(doc, "8. Cuadro comparativo de las referencias y su relación con el proyecto")
    rows = [(f"[{NUM[k]}]", short_name(BY_KEY[k]), BY_KEY[k]["constructo"], C.RESUMEN_ES[k], C.RELACION[k][0], C.RELACION[k][1]) for k in ORDERED]
    t = table(doc, ["Ref.", "Autores (año)", "Constr.", "Aporte principal", "Relación con BioCafe", "Relevancia"], rows, [0.45, 1.3, 0.55, 3.45, 2.85, 0.8], 8)
    no_split_rows(t)
    alta = sum(1 for k in ORDERED if C.RELACION[k][1] == "Alta")
    para(doc, f"Relevancia alta: {alta} referencias; media: {len(ORDERED) - alta}. Alta = aplicable de forma directa a una decisión del proyecto; "
         "media = aporta contexto o una técnica que se usaría solo en un escenario futuro.", 9, before=4)

    back = doc.add_section(WD_SECTION.NEW_PAGE); page_setup(back, 1, 1, 1)
    heading(doc, "9. Evaluación de la revisión: cinco preguntas")
    para(doc, "Las cinco preguntas se tomaron de la lista de calidad de la guía del curso para revisar la propia revisión. Cada respuesta "
         "indica la evidencia y el ajuste que produjo.", 11, after=6)
    table(doc, ["#", "Pregunta", "Respuesta y evidencia", "Ajuste o corrección derivada"],
          [(i, q, a, adj) for i, (q, a, adj) in enumerate(C.PREGUNTAS, 1)], [0.3, 1.6, 2.4, 2.2], 9)

    heading(doc, "10. Ajustes y correcciones de la revisión sistemática")
    para(doc, "Registro ordenado de los cambios hechos durante la revisión, desde la búsqueda hasta la redacción, y de lo que queda pendiente.", 11, after=6)
    table(doc, ["#", "Etapa", "Ajuste o corrección"], [(i, e, txt) for i, (e, txt) in enumerate(C.AJUSTES, 1)], [0.3, 1.0, 5.2], 9)

    heading(doc, "11. Archivos de la solución")
    for name, desc in (("Articulo_IEEE_Revision_MPI_BioCafe.docx", "artículo final en formato IEEE"),
                       ("Trazabilidad_Revision_MPI_BioCafe.docx", "este documento"),
                       ("Semilla_Zotero_Referencias.ris / .bib / .docx", "referencias para importar en Zotero en cualquier equipo, con título, autores, abstract y DOI"),
                       ("01_Constructos_y_prompts.md", "constructos, prompts, cadenas de búsqueda y flujo de selección"),
                       ("datos/ y herramientas/", "evidencia en JSON y scripts que repiten la búsqueda y generan los documentos")):
        p = para(doc, after=2); set_font(p.add_run(name + ": "), 11, bold=True); set_font(p.add_run(desc + "."), 11)
    doc.save(out)

# ---------------------------------------------------------------- seed (Word copy)
def build_seed(out):
    doc = Document(); s = doc.sections[0]; page_setup(s, 1, 1, 1)
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(11)
    para(doc, "Semilla de referencias para Zotero", 18, WD_ALIGN_PARAGRAPH.CENTER, after=4, bold=True)
    para(doc, C.TITULO, 12, WD_ALIGN_PARAGRAPH.CENTER, after=4, italic=True)
    para(doc, "Autoras: " + "; ".join(C.autores_con_id()), 11, WD_ALIGN_PARAGRAPH.CENTER, after=12)
    heading(doc, "Cómo cargar las referencias en cualquier equipo", 2)
    for i, step in enumerate((
        "Instale Zotero (https://www.zotero.org/download/) y ábralo.",
        "En Zotero, elija Archivo > Importar… y seleccione Semilla_Zotero_Referencias.ris (o la versión .bib).",
        "Marque «Colocar las colecciones y elementos importados en una nueva colección». Zotero crea la colección con las "
        f"{len(REFS)} referencias, cada una con título, autores, revista, año, DOI, resumen (abstract) y una etiqueta con su constructo.",
        "Para citar en Word en formato IEEE, instale el complemento de Zotero para Word y elija el estilo «IEEE»."), 1):
        para(doc, f"{i}. {step}", 11, WD_ALIGN_PARAGRAPH.LEFT, after=2)
    para(doc, "Las referencias se cargaron además en la colección «BioCafe - Revisión sistemática MPI» de la biblioteca de las autoras mediante el "
         "MCP de Zotero. El orden y la numeración [n] coinciden con el artículo IEEE.", 11, before=6, after=8)
    heading(doc, "Referencias", 2)
    for k in ORDERED:
        r = BY_KEY[k]
        p = para(doc, before=8, after=2); set_font(p.add_run(f"[{NUM[k]}] {r['titulo']}"), 11, bold=True)
        for label, value in (("Autores: ", "; ".join(f"{a['family']}, {a['given']}".strip(", ") for a in r["autores"])),
                             ("Revista: ", f"{r['revista']} ({r['editorial']}), {r['anio']}"),
                             ("Constructo: ", f"{r['constructo']} {CONS_BY_ID[r['constructo']]['nombre']}")):
            p = para(doc, after=1); set_font(p.add_run(label), 10, bold=True); set_font(p.add_run(value), 10)
        p = para(doc, after=1); set_font(p.add_run("DOI: "), 10, bold=True); add_hyperlink(p, r["url"], r["url"], 10)
        p = para(doc, after=4); set_font(p.add_run("Abstract: "), 10, bold=True); set_font(p.add_run(r["resumen"]), 10)
    doc.save(out)

if __name__ == "__main__":
    (ROOT / "figuras").mkdir(exist_ok=True)
    fig = ROOT / "figuras" / "flujo_seleccion.png"
    flow = flujo_figure(fig)
    build_article(ROOT / "Articulo_IEEE_Revision_MPI_BioCafe.docx", fig)
    build_traceability(ROOT / "Trazabilidad_Revision_MPI_BioCafe.docx", flow)
    build_seed(ROOT / "Semilla_Zotero_Referencias.docx")
    json.dump({k: NUM[k] for k in ORDERED}, open(DATA / "numeracion_ieee.json", "w", encoding="utf8"), indent=1)
    print("ok", flow, "citas:", len(NUM))
