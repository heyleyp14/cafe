# Shortcuts for the ML pipeline. Run from the repository root.
PYTHON ?= .venv/bin/python

# TensorFlow does not find the CUDA libraries that pip installs inside the venv
# (tensorflow[and-cuda]) unless they are on the loader path. Empty on CPU-only setups.
NVIDIA_LIBS := $(shell ls -d $(CURDIR)/ml/.venv/lib/python*/site-packages/nvidia/*/lib 2>/dev/null | paste -sd:)
ifneq ($(NVIDIA_LIBS),)
export LD_LIBRARY_PATH := $(NVIDIA_LIBS):$(LD_LIBRARY_PATH)
endif

.PHONY: data train eval tflite parity colab-bundle

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

# Code-only bundle to upload to Colab/Kaggle together with ml/colab_entrenamiento.ipynb.
colab-bundle:
	rm -f cafe_ml_bundle.zip
	zip -q cafe_ml_bundle.zip ml/config.py ml/requirements.txt ml/0*.py
	@echo "cafe_ml_bundle.zip listo"
