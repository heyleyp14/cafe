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
- [ ] T2 Phase 2 training (`ml/02_entrenar.py`)
- [ ] T3 Phase 3 evaluation and threshold (`ml/03_evaluar.py`)
- [ ] T4 Phase 4 TFLite conversion (`ml/04_convertir_tflite.py`)
- [ ] T5 Phase 5 parity and golden vectors (`ml/05_paridad_tflite.py`)
- [ ] T6 Phase 6 Android project base — needs Android SDK
- [ ] T7 Phase 7 `conditions.json` — needs the report text (sections 1.1, 1.2)
- [ ] T8 Phase 8 classifier
- [ ] T9 Phase 9 UI — needs device or emulator
- [ ] T10 Phase 10 performance and robustness
- [ ] T11 Phase 11 tests — needs device or x86_64 emulator
- [ ] T12 Phase 12 field evaluation and docs — needs a phone and human-taken photos

## Evidence

- T0: tool check and license verification recorded in `docs/bitacora.md` and `docs/decisiones.md` (2026-10-10).
- T0: commit `a514810` on `feat/phase-0-setup`. RDD off (global), so no native review; assessed tier not applicable.

- T1: `ml/outputs/dataset_stats.json` — 2736 images, leakage check 0/0/0, train minimum 260, imbalance 3.919 (crop exclusion reverted on human instruction).

## Known gaps

- GPU works only with the venv `nvidia/*/lib` folders on `LD_LIBRARY_PATH` (the Makefile exports it).
- Android SDK and adb missing; only JDK 21 installed (plan asks for 17).
- The project report (source for phase 7 texts) is not in the repository.

## Next step

T2: write `ml/02_entrenar.py` and a Colab notebook; training and reported numbers come from Colab/Kaggle per plan section 2.
