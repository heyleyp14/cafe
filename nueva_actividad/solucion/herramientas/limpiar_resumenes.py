"""Normalize abstract text in referencias.json (ligatures, duplicated LaTeX, glued words).

Usage: python limpiar_resumenes.py <referencias.json>
Abstracts with words glued together are replaced by the OpenAlex copy when it is clean.
"""
import json, re, sys, urllib.request

def openalex(doi):
    req = urllib.request.Request("https://api.openalex.org/works/https://doi.org/" + doi, headers={"User-Agent": "revision-biocafe"})
    try:
        inv = json.load(urllib.request.urlopen(req, timeout=60)).get("abstract_inverted_index") or {}
    except Exception:
        return ""
    pos = {p: w for w, ps in inv.items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))

def glued(text):
    return any(len(w) > 28 and "/" not in w for w in text.split())

def normalize(text):
    text = text.replace(" ﬁ ", "fi").replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"\$\$\s*([\d.]+)\s*\\times\s*\$\$\s*[\d.]+\s*×", r"\1×", text)   # "$$1.2\times $$ 1.2 ×" -> "1.2×"
    text = re.sub(r"\$(\d+)\$", r"\1", text).replace("\\%", "%").replace("$", "")
    text = re.sub(r"(?<=[a-z])(?=[A-Z][a-z])", "", text)
    return re.sub(r"\s+", " ", text).strip()

path = sys.argv[1]; refs = json.load(open(path, encoding="utf8"))
for r in refs:
    if glued(r["resumen"]):
        alt = normalize(openalex(r["doi"]))
        if alt and not glued(alt):
            r["resumen"], r["fuente_resumen"] = alt, "OpenAlex"
    r["resumen"] = normalize(r["resumen"])
    print("glued" if glued(r["resumen"]) else "ok   ", r["doi"], r["fuente_resumen"])
json.dump(refs, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=1)
