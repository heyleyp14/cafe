"""Citation key shared by the seed files and the Word documents: family name + year + first long title word."""
import re, unicodedata

def key(r):
    family = unicodedata.normalize("NFKD", r["autores"][0]["family"]).encode("ascii", "ignore").decode()
    word = next(w for w in re.findall(r"[A-Za-z]+", r["titulo"]) if len(w) > 3)
    return f"{re.sub(r'[^A-Za-z]', '', family).lower()}{r['anio']}{word.lower()}"
