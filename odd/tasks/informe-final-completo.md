# Informe final BioCafe completo (Protocolo)

Objective: turn `docs/Protocolo de entrega del Documento final de Proyecto_cursos 2026_2 (1).docx` into the complete final report, following the structure of the Malaria report. Branch: main (docx only). Delivery: single file. Runner: none (document); checks are structural readback and PDF render.

## Specs

- S1. "Quiero que sea sobre Protocolo, que quede todo completado, no deben quedar secciones genéricas por completar"
- S2. "todos los objetivos con evidencias, tablas, imagenes de la app, la web promocional en vercel, y todo lo necesario, debe quedar muy completo"
- S3. "falta complementarlo más añadir diagramas, para la estructura y lo que debe tener puede guiarse por el documento llamado \"Informe_Final_Malaria_Rangel_Velandia_Becerra_Medina_v2.docx\""
- S4. Keep the 30 Zotero references added earlier, cited in the body (previous request).

## Tasks

- T1 (S1, S4) Base = content of `docs/Informe_BioCafe_completado.docx` (Protocolo + objectives 3-4), re-apply the 30 Zotero references. Route: inline.
- T2 (S1) Remove template guidance text; add Abstract, keywords, table of contents field. Route: inline.
- T3 (S3) Heading structure like the Malaria report: introduction and justification subsections, one heading per specific objective, verification of objectives, conclusions/recommendations. Route: inline.
- T4 (S2, S3) Diagrams and charts: CRISP-DM vs objectives, architecture, photo flow, training pipeline, decision rules, training curves, external-test comparison. Route: inline.
- T5 (S2) Landing page (Vercel) screenshots and description; app screenshots. Route: inline.
- T6 (S2, S3) Tables: antecedentes, datasets, requirements, components, model contract, tests, objective verification; numbered captions for all figures and tables. Route: inline.

## Log

- L1 (2026-10-29): "Eee falta complementarlo más añadir diagramas, para la estructura y lo que debe tener puede guiarse por el documento llamado \"Informe_Final_Malaria_Rangel_Velandia_Becerra_Medina_v2.docx\" en /home/josue/Documentos/Universidad/sistemas_inteligentes/primer_corte/proyecto-ia/docs"
- L2 (2026-10-29): answer to base-document question: "Quiero que sea sobre Protocolo, que quede todo completado, no deben quedar secciones genéricas por completar, todos los objetivos con evidencias, tablas, imagenes de la app, la web promocional en vercel, y todo lo necesario, debe quedar muy completo"
- L3: Vercel deployment URLs are behind Vercel SSO (302); no public domain found. Landing screenshots are taken from a local production build of the same source.
- L4 (2026-10-30): T1-T6 done inline. Result: 63 pages, 22 numbered figures, 15 numbered tables, 78 references (refs 45-74 Zotero BioCafe, 75-80 general Zotero items), static table of contents with real page numbers, PAGE field in footers (the original had a hard-coded "1"). Checks: PDF render with LibreOffice, no template text or unresolved placeholders, no blank pages, every reference cited except [30] (uncited in the original).
- L5: Fixed in-text numbers that did not match the reference list: Rodríguez-Gallo [5]->[7], AlFrhan y Almaleh [6]->[8], Sandhya/Deep-CofeNet [7]->[27] (list entry was a duplicate "[3]"). Still open for the authors: "Salom Medina y Rosas Ruiz [8]" points to the wrong entry; photo sources of Figures 2-12 unknown.
- Next step: authors review the open items; commit/push only when the user asks.
