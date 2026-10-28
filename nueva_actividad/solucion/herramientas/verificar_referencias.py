"""Verify each selected DOI and collect citation metadata and abstracts.

Usage: python verificar_referencias.py <seleccion.json> <salida.json>
Sources: Crossref (metadata, existence check), then Crossref, Semantic Scholar and
OpenAlex for the abstract. Prints one line per DOI with the checks that failed.
"""
import html, json, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "revision-sistematica-biocafe/1.0 (mailto:josuerangel212@gmail.com)"}
MIN_YEAR = 2022

def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            return json.load(r)
    except Exception:
        return None

def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"^\s*(Abstract|ABSTRACT)\s*", "", html.unescape(text))
    return re.sub(r"\s+", " ", text).strip()

def openalex_abstract(doi):
    w = get("https://api.openalex.org/works/https://doi.org/" + doi)
    inv = (w or {}).get("abstract_inverted_index")
    if not inv: return ""
    pos = {p: word for word, ps in inv.items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))

selection = json.load(open(sys.argv[1], encoding="utf8"))
out = []
for construct, dois in selection.items():
    for doi in dois:
        m = (get("https://api.crossref.org/works/" + urllib.parse.quote(doi)) or {}).get("message")
        if not m:
            print("NO EXISTE", doi); continue
        parts = (m.get("published-print") or m.get("published-online") or m.get("published") or m["issued"])["date-parts"][0]
        abstract, source = clean(m.get("abstract")), "Crossref"
        if len(abstract) < 200:
            s2 = get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=abstract") or {}
            abstract, source = clean(s2.get("abstract")), "Semantic Scholar"
        if len(abstract) < 200:
            abstract, source = clean(openalex_abstract(doi)), "OpenAlex"
        ref = {"constructo": construct, "doi": m["DOI"].lower(), "url": "https://doi.org/" + m["DOI"].lower(),
               "titulo": clean(m["title"][0]), "autores": [{"given": a.get("given", ""), "family": a.get("family", a.get("name", ""))} for a in m.get("author", [])],
               "revista": clean((m.get("container-title") or [""])[0]), "editorial": m.get("publisher", ""),
               "anio": parts[0], "mes": parts[1] if len(parts) > 1 else None,
               "volumen": m.get("volume", ""), "numero": m.get("issue", ""), "paginas": m.get("page", ""),
               "articulo": m.get("article-number", ""), "issn": (m.get("ISSN") or [""])[0],
               "resumen": abstract, "fuente_resumen": source if abstract else "", "tipo": m.get("type")}
        problems = [p for p, bad in (("anio<2022", ref["anio"] < MIN_YEAR), ("sin resumen", not abstract), ("sin autores", not ref["autores"])) if bad]
        print(f"{'OK ' if not problems else 'REV'} {construct} {ref['anio']} {doi} | {ref['fuente_resumen'] or '-'} {len(abstract)}c | {', '.join(problems)}")
        out.append(ref); time.sleep(3)
json.dump(out, open(sys.argv[2], "w", encoding="utf8"), ensure_ascii=False, indent=1)
