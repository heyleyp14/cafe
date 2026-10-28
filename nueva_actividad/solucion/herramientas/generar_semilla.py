"""Write the Zotero seed files (.bib and .ris) from referencias.json and constructos.json.

Usage: python generar_semilla.py <datos dir> <output dir>
Both files carry title, authors, abstract, DOI link and the construct as a keyword,
so any Zotero installation can import them (File > Import).
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from claves import key

data, out = Path(sys.argv[1]), Path(sys.argv[2])
refs = json.load(open(data / "referencias.json", encoding="utf8"))
constructs = {c["id"]: c["nombre"] for c in json.load(open(data / "constructos.json", encoding="utf8"))}

def tex(s):
    return re.sub(r"([&%#_])", r"\\\1", s)

def pages(r):
    return r["paginas"] or r["articulo"]

bib, ris = [], []
for r in refs:
    tag = f"{r['constructo']} {constructs[r['constructo']]}"
    fields = {"title": "{" + tex(r["titulo"]) + "}", "author": " and ".join(f"{a['family']}, {a['given']}".strip(", ") for a in r["autores"]),
              "journal": tex(r["revista"]), "year": str(r["anio"]), "volume": r["volumen"], "number": r["numero"], "pages": pages(r),
              "doi": r["doi"], "url": r["url"], "issn": r["issn"], "publisher": tex(r["editorial"]),
              "abstract": tex(r["resumen"]), "keywords": tex(tag)}
    bib.append(f"@article{{{key(r)},\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items() if v) + "\n}\n")
    lines = ["TY  - JOUR", f"TI  - {r['titulo']}"] + [f"AU  - {a['family']}, {a['given']}".rstrip(", ") for a in r["autores"]]
    lines += [f"T2  - {r['revista']}", f"PY  - {r['anio']}", f"VL  - {r['volumen']}", f"IS  - {r['numero']}", f"SP  - {pages(r)}",
              f"DO  - {r['doi']}", f"UR  - {r['url']}", f"SN  - {r['issn']}", f"PB  - {r['editorial']}", f"AB  - {r['resumen']}", f"KW  - {tag}", "ER  - "]
    ris.append("\n".join(l for l in lines if not re.match(r"^[A-Z0-9]{2}  - $", l) or l == "ER  - ") + "\n")
(out / "Semilla_Zotero_Referencias.bib").write_text("\n".join(bib), encoding="utf8")
(out / "Semilla_Zotero_Referencias.ris").write_text("\n".join(ris), encoding="utf8")
print(len(bib), "entradas")
