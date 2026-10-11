# Shortcuts for the ML pipeline. Run from the repository root.
PYTHON ?= .venv/bin/python
# Training run to work on: every run keeps its files in ml/outputs/$(RUN)/.
RUN ?= final

# TensorFlow does not find the CUDA libraries that pip installs inside the venv
# (tensorflow[and-cuda]) unless they are on the loader path. Empty on CPU-only setups.
NVIDIA_LIBS := $(shell ls -d $(CURDIR)/ml/.venv/lib/python*/site-packages/nvidia/*/lib 2>/dev/null | paste -sd:)
ifneq ($(NVIDIA_LIBS),)
export LD_LIBRARY_PATH := $(NVIDIA_LIBS):$(LD_LIBRARY_PATH)
endif

.PHONY: data train eval tflite parity results colab-bundle colab-data

data:
	cd ml && $(PYTHON) 01_preparar_datos.py

train:
	cd ml && $(PYTHON) 02_entrenar.py --run $(RUN)

eval:
	cd ml && $(PYTHON) 03_evaluar.py --run $(RUN)

tflite:
	cd ml && $(PYTHON) 04_convertir_tflite.py --run $(RUN)

parity:
	cd ml && $(PYTHON) 05_paridad_tflite.py --run $(RUN)

results:
	cd ml && $(PYTHON) generar_resultados.py

# Code-only bundle to upload to Colab/Kaggle together with ml/colab_entrenamiento.ipynb.
colab-bundle:
	cd ml && $(PYTHON) crear_bundle.py

# Processed images for the v2 training on Colab (ml/colab_run_v2.py).
colab-data:
	cd ml && $(PYTHON) crear_bundle.py --data
