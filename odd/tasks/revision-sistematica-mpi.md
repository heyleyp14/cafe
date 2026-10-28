# Revisión sistemática descriptiva (MPI, computación paralela y sistemas inteligentes) aplicada a BioCafe

Objetivo: artículo corto IEEE (≤10 páginas), documento de trazabilidad y semilla de Zotero en `nueva_actividad/solucion/`.
Rama: `feat/revision-sistematica-mpi`. Entrega: `single-pr` (solo documentación). Pruebas: no hay RED ejecutable; se validan DOI contra Crossref y la estructura de los .docx.

## Specs
- S1 "Cree un documento de Word usando normas IEEE" — producto final con "titulo, autores, afiliación, resumen, abstract, introducción, materiales y métodos, resultados y discusión y conclusiones y referencias"; "artículo corto de nomas de 10 páginas"; "es una revisión descriptiva sistemática de literatura, importante que sea descriptiva".
- S2 Segundo archivo Word: "el de las referencias en WORD donde debe ir el resumen, abstract y cuadros etc (es como de trazabilidad del proyecto)"; "hacer un cuadro comparativo para ver cómo está relacionado esas referencias con el proyecto esto debe ir dentro del segundo archivo"; "Relacionar los resúmenes mostrados en el archivo anexo como benefician al proyecto (esto cada dos o tres en grupos)"; "Se deben hacer 5 preguntas ... evaluar o revisar la revisión sistémica, en el segundo documento"; "Se debe organizar lógicamente, quiere decir que mande los ajustes o las correcciones de la revisión sistémica."
- S3 Tercer archivo: "el de zotero para exportar las referencias que se usen. Debe usar el MCP de zotero, creando un documento que me permita cargar (como un seed), en cualquier pc las referencias"; "título, autores, abstract debe ser incluidos en el documento tipo seed, ESE DOCUMENTO TAMBIÉN DEBE ESTAR EN WORD".
- S4 Referencias: "deben solo las que consulte para este documento, NO incluir las que están ya a menos que coincidencialmente sea la misma"; "toda referencias que use debe tener enlace DOI, y en verdad existir, y ser menor a 5 años de antiguedad"; "En lo posible que sean artículos de ScienceDirect".
- S5 Contenido: "debe incluir conceptos de Fundamentos de Computación Paralela y Distribuída y Sistemas Inteligentes"; tema según `nueva_actividad/docs`: "revisión sistémica sobre MPI ... aplicado a su proyecto de investigación".
- S6 "Los prompts que use para buscar dichas referencias, deben salir de los constructos, por lo que debe dejarlos documentados (en un documento .md)"; "se debe ir pidiendo referencias en base a los constructos".
- S7 Todo "dentro de la carpeta de nueva_actividad/solucion".
- Supuesto A1: el "archivo anexo" con los resúmenes es el segundo documento (trazabilidad), donde se muestran los resúmenes de las referencias.
- Supuesto A2: proyecto = BioCafe (detección temprana de plagas y enfermedades del café); autoras y afiliación tomadas del póster.
- Supuesto A3: "menor a 5 años" = publicadas desde 2022-01-01 (fecha de trabajo 2026-10-27).

## Tasks
- T1 S5,S6 constructos y prompts (.md) — inline — hecho (`01_Constructos_y_prompts.md`)
- T2 S4,S6 búsqueda y verificación de referencias (Crossref) — inline — hecho (28 refs, 2022-2026, DOI verificado)
- T3 S3,S4 colección en Zotero vía MCP + semilla .ris/.bib/.docx — inline — hecho (colección EQAD4V6F, 28/28)
- T4 S1,S5 artículo IEEE .docx — inline — hecho (5 páginas en OnlyOffice)
- T5 S2 documento de trazabilidad .docx — inline — hecho (20 páginas)
- T6 S1-S7 verificación y commit — inline — hecho (`herramientas/verificar_entrega.py`: 25/25 OK)

## Log
- L1 (2026-10-27) Pedido original del usuario (texto completo en la conversación; fragmentos citados en S1-S6).
- L2 (2026-10-27) No había MCP de Zotero; el usuario eligió "Instalar zotero-mcp (Recomendado)". Se registró `zotero-mcp` v0.15.1 (modo local, escritura autorizada). Biblioteca existente: colección "Malaria - Proyecto".
- L3 (2026-10-27) ScienceDirect bloquea la lectura automática y no comparte resúmenes con APIs abiertas: 22 candidatos sin resumen se reemplazaron por otros del mismo constructo (16 de 28 finales son de ScienceDirect). Ninguna referencia estaba antes en la biblioteca de Zotero (búsqueda por DOI vía MCP).
- L4 (2026-10-27) Verificación: 28 DOI resuelven en doi.org; artículo de 5 páginas (render OnlyOffice, no probado en Word); correos de las autoras pendientes.
- L5 (2026-10-27) Usuario: "Heyley Yurani Parada Parada 1093887319 / Lisbeth Gissel Cordero Tovar 1093293375"; eligió «En los tres documentos (Recomendado)». Se agregó la identificación bajo cada nombre en el artículo, la portada y la tabla de la trazabilidad y la semilla Word.
- L6 (2026-10-27) Usuario: "heyley.paradapar@unipamplona.edu.co, lisbeth.corderotov@unipamplona.edu.co". Correos agregados en los tres documentos (enlace mailto en el artículo); se cierra el pendiente de correos.
