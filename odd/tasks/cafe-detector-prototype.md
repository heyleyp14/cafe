# Feature: cafe-detector-prototype

Locator: `odd/tasks/cafe-detector-prototype.md` · Engram topic: `odd/cafe-detector-prototype/tasks`

## Objective

Implement the coffee-leaf pest/disease classifier prototype end to end, phase by phase, as specified in `PLAN_Prototipo_Cafe_Kotlin.md`.

## Constraints

- Phases run in order; a phase closes only when its acceptance criteria are observed.
- Section 4 contract: float32 `[1,224,224,3]` RGB 0–255 input, normalization inside the model, squash resize, softmax output, `labels.txt` order.
- Never invent numbers; write "NO EJECUTADO" with the reason. Stop and ask when a dataset, tool or network access is missing.
- No datasets or keys in git, no `INTERNET` permission, no in-app normalization, no management advice outside the report.
- Each phase closes with an update to `docs/bitacora.md`. Decisions go to `docs/decisiones.md`.
- Project docs and UI strings are Spanish (plan convention); code identifiers and comments are English.

## Delivery

Strategy `ask-on-risk`. Forecast exceeds 400 authored lines (ML scripts plus Android app), so the chain strategy must be asked before the second work-unit commit. Branch: `feat/phase-0-setup`.

## Tasks

- [x] T0 Phase 0 environment — route: inline (mechanical files). Unblocked with uv + CPython 3.12.8 venv at `ml/.venv`; install and TFLite conversion smoke test observed.
- [x] T1 Phase 1 data preparation (`ml/01_preparar_datos.py`) — route: inline (one script). Test-first exception: no deterministic expected output existed before inspecting the datasets; checked through the leakage verification built into the script plus an independent recount.
- [x] T2 Phase 2 training (`ml/02_entrenar.py`) — run on Colab T4 via google-colab-cli; acceptance observed from ml/outputs
- [x] T3 Phase 3 evaluation and threshold (`ml/03_evaluar.py`) — run on Colab T4 via google-colab-cli; acceptance observed from ml/outputs
- [x] T4 Phase 4 TFLite conversion (`ml/04_convertir_tflite.py`) — run on Colab T4 via google-colab-cli; acceptance observed from ml/outputs
- [x] T5 Phase 5 parity and golden vectors (`ml/05_paridad_tflite.py`) — run on Colab T4 via google-colab-cli; acceptance observed from ml/outputs
- [x] T6 Phase 6 Android project base — route: inline; `assembleDebug` builds, app opens on the API 37 emulator, no INTERNET permission
- [x] T7 Phase 7 `conditions.json` — route: inline; texts copied from the report in docs/, unit test green
- [x] T8 Phase 8 classifier — route: inline; app ships the fp32 model (human decision); unit 8/8, instrumented 4/4 on the emulator (level 1 max diff 1.7e-6, level 2 10/10)
- [x] T9 Phase 9 UI — route: delegated writer (7 new files); parent verified camera, gallery, rotation and permission-denied flows on the emulator
- [x] T10 Phase 10 performance and robustness — route: inline; robustness tests green, library-added permissions removed, thread comparison inconclusive on emulator
- [x] T11 Phase 11 tests — unit 11/11, instrumented 9/9 on the x86_64 emulator
- [ ] T12 Phase 12 field evaluation and docs — resultados.md generator and README done; field steps 1-3 pending (need the human's phone and real photos)

## Evidence

- T0: tool check and license verification recorded in `docs/bitacora.md` and `docs/decisiones.md` (2026-10-10).
- T0: commit `a514810` on `feat/phase-0-setup`. RDD off (global), so no native review; assessed tier not applicable.

- T1: `ml/outputs/dataset_stats.json` — 2736 images, leakage check 0/0/0, train minimum 260, imbalance 3.919 (crop exclusion reverted on human instruction).

- T2-T5: Colab run 2026-10-10 — test accuracy 0.9561, F1 macro 0.9587, threshold 0.40 (accepts 100%), quantized parity 0.98, model.tflite 2531920 bytes.

## Known gaps

- GPU works only with the venv `nvidia/*/lib` folders on `LD_LIBRARY_PATH` (the Makefile exports it).

## Next step

T12 field evaluation: needs the human's physical phone over adb and real leaf photos; then docs/resultados.md and README. Open questions for the human: version golden images in git; SANAS_ROCOLE exclusion.
