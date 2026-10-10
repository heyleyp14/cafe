# Shortcuts for the ML pipeline. Run from the repository root.
PYTHON ?= python

.PHONY: data train eval tflite parity

data:
	cd ml && $(PYTHON) 01_preparar_datos.py

train:
	cd ml && $(PYTHON) 02_entrenar.py

eval:
	cd ml && $(PYTHON) 03_evaluar.py

tflite:
	cd ml && $(PYTHON) 04_convertir_tflite.py

parity:
	cd ml && $(PYTHON) 05_paridad_tflite.py
