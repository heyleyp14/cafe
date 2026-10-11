# Feature: model-v2-retraining

Locator: `odd/tasks/model-v2-retraining.md` · Engram topic: `odd/model-v2-retraining/tasks` · Plan: `docs/PLAN_reentrenamiento_v2.md`

## Objective

Retrain the three-class model so it generalizes beyond its training datasets, with an evaluation that cannot be fooled by source imbalance or leakage.

## Constraints

- Three classes only (human decision, 2026-10-10). Section 4 contract and section 0 rules of the original plan still apply.
- Training runs on Colab. The final holdout (JMuBEN) is evaluated once, in R5.
- No target number is promised; measure and report.

## Tasks

- [x] R0 Diagnosis — route: inline. Split of v1 is source-skewed (RoCoLe 67% of train, about 3% of val/test); background replacement does not change BRACOL accuracy; leaf cropping lowers it to 0.509.
- [x] R1 Evaluation design — route: delegated writer; source-and-class stratified split (test RED then GREEN, worst deviation 0.0042); holdout download in progress
- [x] R2 Data — 3596 images, BRACOL added (MD5-only dedup), stratum sample weights
- [x] R3 Robustness — stronger augmentation in the data pipeline; background replacement not implemented
- [ ] R4 Training on Colab: full fine-tuning, MobileNetV2 vs EfficientNet-B0, calibration and threshold
- [ ] R5 Close: conversion, parity, emulator and phone tests, open the final holdout once

## Evidence

- R0: `docs/bitacora.md`, section "Reentrenamiento v2 — R0".

## Next step

R4: needs a Colab T4 session; upload `cafe_ml_bundle.zip` and `cafe_data_v2.zip`, run `ml/colab_run_v2.py` (stage 1, both architectures, BRACOL held out).
