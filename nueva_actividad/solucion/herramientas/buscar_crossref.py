"""Run each construct's queries against Crossref and save the candidates.

Usage: python buscar_crossref.py <constructos.json> <salida.json> [filas]
Filters: journal articles published from 2022-01-01. Each query runs twice:
restricted to Elsevier (ScienceDirect, DOI prefix 10.1016) and without that restriction.
"""
import json, sys, time, urllib.parse, urllib.request
from datetime import date

API = "https://api.crossref.org/works"
HEADERS = {"User-Agent": "revision-sistematica-biocafe/1.0 (mailto:josuerangel212@gmail.com)"}

def query(text, rows, elsevier):
    filt = "from-pub-date:2022-01-01,type:journal-article" + (",prefix:10.1016" if elsevier else "")
    params = {"query.bibliographic": text, "filter": filt, "rows": rows,
              "select": "DOI,title,published,container-title,author,publisher,is-referenced-by-count"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        msg = json.load(r)["message"]
    return msg["total-results"], msg["items"]

constructs = json.load(open(sys.argv[1], encoding="utf8"))
rows = int(sys.argv[3]) if len(sys.argv) > 3 else 8
log = {"fecha": date.today().isoformat(), "base": "Crossref REST API (api.crossref.org)", "busquedas": []}
for c in constructs:
    for q in c["consultas"]:
        for elsevier in (True, False):
            total, items = query(q, rows, elsevier)
            log["busquedas"].append({
                "constructo": c["id"], "consulta": q, "filtro": "ScienceDirect (10.1016)" if elsevier else "todas las editoriales",
                "resultados_totales": total,
                "candidatos": [{"doi": i["DOI"], "titulo": (i.get("title") or [""])[0], "anio": i["published"]["date-parts"][0][0],
                                "revista": (i.get("container-title") or [""])[0], "citas": i.get("is-referenced-by-count", 0)} for i in items]})
            time.sleep(1)
json.dump(log, open(sys.argv[2], "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("busquedas:", len(log["busquedas"]))
