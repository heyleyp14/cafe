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
- [ ] R1 Evaluation design: class-and-source stratified group split; final holdout; leave-one-source-out validation
- [ ] R2 Data: add BRACOL, group by leaf and source, balanced sampling
- [ ] R3 Robustness: stronger augmentation
- [ ] R4 Training on Colab: full fine-tuning, MobileNetV2 vs EfficientNet-B0, calibration and threshold
- [ ] R5 Close: conversion, parity, emulator and phone tests, open the final holdout once

## Evidence

- R0: `docs/bitacora.md`, section "Reentrenamiento v2 — R0".

## Next step

R1: fix the split in `ml/01_preparar_datos.py` (stratify by class and source), download JMuBEN as the untouched final holdout.
