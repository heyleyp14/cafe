"""Check the deliverables: required sections, citations, DOI links (doi.org must redirect) and seed contents.

Usage: python verificar_entrega.py <solucion dir>
"""
import json, re, sys, urllib.request
from pathlib import Path
from docx import Document

root = Path(sys.argv[1]); refs = json.load(open(root / "datos/referencias.json", encoding="utf8"))
fails = []
def check(cond, msg): print(("OK   " if cond else "FAIL ") + msg); cond or fails.append(msg)

def text_and_links(path):
    d = Document(path); rels = d.part.rels
    links = [r.target_ref for r in rels.values() if "hyperlink" in r.reltype]
    text = "\n".join(p.text for p in d.paragraphs) + "\n".join(c.text for t in d.tables for row in t.rows for c in row.cells)
    return text, links

art, art_links = text_and_links(root / "Articulo_IEEE_Revision_MPI_BioCafe.docx")
for s in ("Resumen—", "Abstract—", "I. Introducción", "II. Materiales y métodos", "III. Resultados y discusión", "IV. Conclusiones", "Referencias", "Universidad de Pamplona", "Heyley Yurani Parada Parada"):
    check(s in art, f"artículo contiene «{s}»")
cited = {int(n) for g in re.findall(r"\[(\d+(?:\], \[\d+)*)\]", art) for n in re.findall(r"\d+", g)}
check(cited == set(range(1, len(refs) + 1)), f"artículo cita [1]..[{len(refs)}] y nada más ({len(cited)} números)")
check(all(f"https://doi.org/{r['doi']}" in art_links for r in refs), "cada referencia del artículo tiene enlace DOI")
check(all(r["anio"] >= 2022 for r in refs), "todas las referencias son de 2022 o posteriores")

tra, _ = text_and_links(root / "Trazabilidad_Revision_MPI_BioCafe.docx")
for s in ("2. Resumen y abstract", "3. Constructos", "4. Prompts", "6. Fichas", "7. Relación de los resúmenes", "8. Cuadro comparativo", "9. Evaluación de la revisión: cinco preguntas", "10. Ajustes y correcciones"):
    check(s in tra, f"trazabilidad contiene «{s}»")
check(len(re.findall(r"^Grupo \d+\.", tra, re.M)) >= 8, "trazabilidad agrupa los resúmenes de 2 o 3")

seed, seed_links = text_and_links(root / "Semilla_Zotero_Referencias.docx")
check(all(r["titulo"] in seed and r["resumen"][:80] in seed for r in refs), "semilla Word: título y abstract de cada referencia")
ris = (root / "Semilla_Zotero_Referencias.ris").read_text(encoding="utf8"); bib = (root / "Semilla_Zotero_Referencias.bib").read_text(encoding="utf8")
check(ris.count("ER  -") == len(refs) and ris.count("AB  -") == len(refs) and ris.count("DO  -") == len(refs), "semilla RIS: 28 registros con abstract y DOI")
check(bib.count("@article{") == len(refs) and bib.count("abstract = {") == len(refs), "semilla BibTeX: 28 entradas con abstract")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
opener = urllib.request.build_opener(NoRedirect)
bad = []
for r in refs:
    try:
        opener.open(urllib.request.Request(f"https://doi.org/{r['doi']}", method="HEAD"), timeout=30); code = 200
    except urllib.error.HTTPError as e:
        code = e.code
    if code not in (301, 302, 303, 307, 308): bad.append((r["doi"], code))
check(not bad, f"los {len(refs)} DOI resuelven en doi.org {bad if bad else ''}")
print("FALLOS:", len(fails))
sys.exit(1 if fails else 0)
