"""Write 01_Constructos_y_prompts.md from the JSON evidence in datos/.

Usage: python generar_md_prompts.py <datos dir> <salida.md>
"""
import json, sys
from pathlib import Path

d = Path(sys.argv[1])
cons = json.load(open(d / "constructos.json", encoding="utf8"))
busq = json.load(open(d / "busqueda_crossref.json", encoding="utf8"))
refs = json.load(open(d / "referencias.json", encoding="utf8"))
crib = json.load(open(d / "cribado.json", encoding="utf8"))
uniq = {x["doi"] for s in busq["busquedas"] for x in s["candidatos"]}
pre = [x for v in json.load(open(d / "preseleccion.json", encoding="utf8")).values() for x in v]
from_v1 = [x for x in pre if x not in uniq]
no_abs = crib["excluidos_sin_resumen"]; excl_abs = len(no_abs)
excl_red = len(crib["no_elegidos_con_resumen"])
assessed = len(set(pre))

L = ["# Constructos y prompts de búsqueda",
     "",
     "Revisión sistemática descriptiva: *Detección temprana de plagas y enfermedades del café con sistemas inteligentes y computación paralela y distribuida*.",
     "",
     f"Fecha de las búsquedas: {busq['fecha']}. Base consultada: {busq['base']}, que indexa ScienceDirect (Elsevier), IEEE, Springer, MDPI y otras editoriales. "
     "Todos los datos de este documento salen de los archivos de `datos/`; los scripts de `herramientas/` permiten repetir el proceso.",
     "",
     "## 1. De dónde salen los constructos",
     "",
     "El proyecto «Sistema de detección temprana de plagas y enfermedades en cultivos de café» (prototipo BioCafe) clasifica fotos de hojas de café "
     "(sana, roya, minador y arañita roja) con una red EfficientNet-B0 que se entrena en GPU y se ejecuta en el teléfono. Los constructos se derivaron "
     "del título y de los componentes del proyecto: el problema agrícola (C1, C2), el sistema inteligente (C3 a C5) y la computación paralela y "
     "distribuida que lo soporta (C6 a C8). La revisión trata sobre el proyecto, no sobre una tecnología en particular.",
     "",
     "| ID | Constructo | Área | Definición operativa | Indicadores |",
     "|---|---|---|---|---|"]
L += [f"| {c['id']} | {c['nombre']} | {c['area']} | {c['definicion']} | {c['indicadores']} |" for c in cons]
L += ["", "## 2. Prompts y cadenas de búsqueda por constructo", "",
      "Cada prompt expresa el pedido de referencias que nace del constructo; las cadenas son su traducción a la consulta bibliográfica que se ejecutó. "
      "Cada cadena se lanzó dos veces: limitada a ScienceDirect (prefijo DOI 10.1016) y sin límite de editorial. "
      "Filtros comunes: artículos de revista (`type:journal-article`) publicados desde el 2022-01-01 (menos de 5 años).", ""]
for c in cons:
    L += [f"### {c['id']}. {c['nombre']}", "", f"**Prompt:** {c['prompt']}", "", "| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |", "|---|---|---:|---:|"]
    L += [f"| `{s['consulta']}` | {s['filtro']} | {s['resultados_totales']:,} | {len(s['candidatos'])} |".replace(",", ".")
          for s in busq["busquedas"] if s["constructo"] == c["id"]]
    inc = [r for r in refs if r["constructo"] == c["id"]]
    L += ["", "Referencias incluidas:", ""] + [f"- {r['titulo']} ({r['anio']}). https://doi.org/{r['doi']}" for r in inc] + [""]
L += ["## 3. Criterios de selección", "",
      "**Inclusión:** artículo de revista; publicado desde 2022; DOI que resuelve en Crossref; resumen recuperable (Crossref, Semantic Scholar u OpenAlex); "
      "relación directa con un constructo; preferencia por ScienceDirect.",
      "",
      "**Exclusión:** ruido semántico de la búsqueda (por ejemplo, *message passing* en redes de grafos o *point cloud overlap*); fecha anterior a 2022 o posterior a la de la búsqueda; "
      "sin resumen recuperable; redundancia con otro trabajo ya incluido del mismo constructo; fuera del alcance de clasificación de imágenes o de MPI; "
      "presencia previa en la biblioteca de Zotero del usuario (no hubo coincidencias).",
      "",
      "## 4. Flujo de selección", "",
      "| Etapa | Registros |", "|---|---:|",
      f"| Búsquedas ejecutadas (cadenas × filtros) | {len(busq['busquedas'])} |",
      f"| Registros revisados (10 por búsqueda) | {sum(len(s['candidatos']) for s in busq['busquedas'])} |",
      f"| Registros únicos | {len(uniq)} |",
      f"| Añadidos de la primera búsqueda (versión MPI, ver `datos/v1_mpi/`) | {len(from_v1)} |",
      f"| Preseleccionados por título, revista y año, con verificación de DOI | {assessed} |",
      f"| Excluidos por no tener resumen recuperable | {excl_abs} |",
      f"| Excluidos por redundancia o alcance | {excl_red} |",
      f"| **Incluidos** | **{len(refs)}** |", "",
      f"De los {len(refs)} incluidos, {sum(r['doi'].startswith('10.1016/') for r in refs)} son de ScienceDirect (Elsevier). "
      f"De los {excl_abs} excluidos por no tener resumen, {sum(x.startswith('10.1016/') for x in no_abs)} son de ScienceDirect: esa editorial bloquea la lectura automática de sus páginas y no comparte sus resúmenes con las APIs abiertas. "
      "Cada constructo quedó cubierto con otros artículos que sí tienen resumen.",
      "", "Motivos de los excluidos por redundancia o alcance:", ""]
L += [f"- https://doi.org/{k}: {v}" for k, v in crib["no_elegidos_con_resumen"].items()]
L += ["", "## 5. Cómo repetir el proceso", "", "```bash",
      "python3 herramientas/buscar_crossref.py datos/constructos.json datos/busqueda_crossref.json 8",
      "python3 herramientas/verificar_referencias.py datos/preseleccion.json datos/preseleccion_verificada.json",
      "python3 herramientas/limpiar_resumenes.py datos/referencias.json",
      "python3 herramientas/generar_semilla.py datos .",
      "python3 herramientas/generar_md_prompts.py datos 01_Constructos_y_prompts.md",
      "```", "",
      "Crossref ordena por relevancia y su índice cambia con el tiempo; repetir la búsqueda otro día puede dar totales y órdenes algo distintos.", ""]
Path(sys.argv[2]).write_text("\n".join(L), encoding="utf8")
print("ok", assessed, excl_abs, excl_red)
