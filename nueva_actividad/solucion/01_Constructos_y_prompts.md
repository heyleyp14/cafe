# Constructos y prompts de búsqueda

Revisión sistemática descriptiva: *Computación paralela con MPI y sistemas inteligentes para la detección temprana de enfermedades en hojas de café*.

Fecha de las búsquedas: 2026-10-27. Base consultada: Crossref REST API (api.crossref.org), que indexa ScienceDirect (Elsevier), IEEE, Springer, MDPI y otras editoriales. Todos los datos de este documento salen de los archivos de `datos/`; los scripts de `herramientas/` permiten repetir el proceso.

## 1. De dónde salen los constructos

El proyecto BioCafe clasifica fotos de hojas de café (sana, roya, minador y arañita roja) con una red EfficientNet-B0 que se entrena en GPU y se ejecuta en el teléfono. La actividad pide revisar MPI aplicado al proyecto, siguiendo las unidades del curso: fundamentación MPI, instalación y configuración sobre una red LAN y sobre un clúster, comunicación punto a punto y comunicación colectiva. Los constructos cruzan esas unidades (Fundamentos de Computación Paralela y Distribuida) con los componentes inteligentes del proyecto (Sistemas Inteligentes).

| ID | Constructo | Área | Definición operativa | Indicadores |
|---|---|---|---|---|
| C1 | Paradigma de paso de mensajes (MPI) | Computación paralela y distribuida | Modelo de programación en memoria distribuida en el que procesos independientes cooperan intercambiando mensajes explícitos mediante el estándar MPI. | rutinas MPI usadas; número de procesos; latencia y ancho de banda de comunicación |
| C2 | Comunicación punto a punto y colectiva | Computación paralela y distribuida | Operaciones de envío/recepción entre pares (Send/Recv) y operaciones que involucran a todos los procesos (Bcast, Reduce, Allreduce, Gather). | tiempo de Allreduce; solapamiento cómputo-comunicación; algoritmo colectivo |
| C3 | Entrenamiento distribuido de redes neuronales profundas | Computación paralela y distribuida + Sistemas inteligentes | Reparto del entrenamiento de un modelo entre varios procesos o GPU (paralelismo de datos o de modelo) con sincronización de gradientes. | aceleración (speedup); eficiencia de escalado; exactitud final frente al entrenamiento secuencial |
| C4 | Aceleración con GPU y programación híbrida (MPI + OpenMP/CUDA) | Computación paralela y distribuida | Combinación de paralelismo entre nodos (MPI), entre hilos (OpenMP) y en el acelerador (CUDA) para aprovechar hardware heterogéneo. | uso de GPU; tiempo por época; modelo de programación híbrido |
| C5 | Infraestructura de clúster y red LAN para MPI | Computación paralela y distribuida | Instalación y configuración de un entorno MPI sobre nodos conectados en red local o en un clúster/HPC, incluida la planificación de trabajos. | número de nodos; interconexión; herramientas de despliegue (contenedores, gestor de trabajos) |
| C6 | Visión por computador con CNN para enfermedades y plagas de cultivos | Sistemas inteligentes | Clasificación o detección de afectaciones en imágenes de hojas mediante redes neuronales convolucionales y aprendizaje por transferencia. | exactitud; F1; número de clases; dataset usado |
| C7 | Inferencia eficiente en el borde (dispositivos móviles) | Sistemas inteligentes + Computación distribuida | Ejecución local de modelos ligeros en teléfonos o dispositivos IoT, sin depender de conexión, con técnicas de compresión y cuantización. | latencia por imagen; tamaño del modelo; consumo de recursos |
| C8 | Aprendizaje federado y sistemas distribuidos en agricultura | Sistemas inteligentes + Computación distribuida | Entrenamiento colaborativo de modelos entre varios nodos o fincas que comparten parámetros en lugar de datos. | número de clientes; rondas de comunicación; exactitud global |

## 2. Prompts y cadenas de búsqueda por constructo

Cada prompt expresa el pedido de referencias que nace del constructo; las cadenas son su traducción a la consulta bibliográfica que se ejecutó. Cada cadena se lanzó dos veces: limitada a ScienceDirect (prefijo DOI 10.1016) y sin límite de editorial. Filtros comunes: artículos de revista (`type:journal-article`) publicados desde el 2022-01-01 (menos de 5 años).

### C1. Paradigma de paso de mensajes (MPI)

**Prompt:** Con base en el constructo «Paradigma de paso de mensajes (MPI)» del proyecto BioCafe, busca artículos de revista publicados desde 2022, con DOI y preferiblemente de ScienceDirect, que analicen cómo se configura y optimiza el rendimiento de aplicaciones MPI (número de procesos, algoritmos colectivos, ubicación de procesos).

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `MPI message passing interface performance` | ScienceDirect (10.1016) | 192.572 | 8 |
| `MPI message passing interface performance` | todas las editoriales | 760.023 | 8 |
| `MPI parallel programming HPC applications` | ScienceDirect (10.1016) | 120.696 | 8 |
| `MPI parallel programming HPC applications` | todas las editoriales | 467.492 | 8 |

Referencias incluidas:

- Simulation-based optimization and sensibility analysis of MPI applications: Variability matters (2022). https://doi.org/10.1016/j.jpdc.2022.04.002
- Tuned your MPI library? Now check the performance guidelines (2026). https://doi.org/10.1016/j.parco.2026.103205
- Using long vector extensions for MPI reductions (2022). https://doi.org/10.1016/j.parco.2021.102871

### C2. Comunicación punto a punto y colectiva

**Prompt:** Con base en el constructo «Comunicación punto a punto y colectiva», busca artículos desde 2022, con DOI, que evalúen operaciones MPI Send/Recv no bloqueantes y colectivas (Bcast, Reduce, Allreduce), su modelado y su efecto en el tiempo de entrenamiento de redes neuronales.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `MPI collective communication allreduce optimization` | ScienceDirect (10.1016) | 87.184 | 8 |
| `MPI collective communication allreduce optimization` | todas las editoriales | 534.339 | 8 |
| `point-to-point communication MPI overlap` | ScienceDirect (10.1016) | 31.127 | 8 |
| `point-to-point communication MPI overlap` | todas las editoriales | 307.523 | 8 |

Referencias incluidas:

- SUARA: A scalable universal allreduce communication algorithm for acceleration of parallel deep learning applications (2024). https://doi.org/10.1016/j.jpdc.2023.104767
- Optimizing MPI collective operations for intra-node shared memory exploitation and oversubscription (2026). https://doi.org/10.1016/j.parco.2026.103207
- Analyzing the impact of the MPI allreduce in distributed training of convolutional neural networks (2023). https://doi.org/10.1007/s00607-021-01029-2
- Towards Efficient HPC: Exploring Overlap Strategies Using MPI Non-Blocking Communication (2025). https://doi.org/10.3390/math13111848
- Detailed Modeling of Heterogeneous and Contention-Constrained Point-to-Point MPI Communication (2023). https://doi.org/10.1109/tpds.2023.3253881

### C3. Entrenamiento distribuido de redes neuronales profundas

**Prompt:** Con base en el constructo «Entrenamiento distribuido de redes neuronales profundas», busca artículos desde 2022, con DOI, que comparen paralelismo de datos, de modelo y en tubería (pipeline) para entrenar redes convolucionales de clasificación de imágenes, incluidas herramientas como Horovod sobre MPI.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `distributed deep learning training data parallelism` | ScienceDirect (10.1016) | 261.701 | 8 |
| `distributed deep learning training data parallelism` | todas las editoriales | 1.675.859 | 8 |
| `Horovod MPI distributed training GPU` | ScienceDirect (10.1016) | 26.941 | 8 |
| `Horovod MPI distributed training GPU` | todas las editoriales | 235.832 | 8 |

Referencias incluidas:

- Study of Data and Model parallelism in Distributed Deep learning for Diabetic retinopathy classification (2023). https://doi.org/10.1016/j.procs.2023.01.201
- Optimizing DNN training with pipeline model parallelism for enhanced performance in embedded systems (2024). https://doi.org/10.1016/j.jpdc.2024.104890
- A Survey on Auto-Parallelism of Large-Scale Deep Learning Training (2023). https://doi.org/10.1109/tpds.2023.3281931
- A snapshot of parallelism in distributed deep learning training (2024). https://doi.org/10.29375/25392115.5054

### C4. Aceleración con GPU y programación híbrida (MPI + OpenMP/CUDA)

**Prompt:** Con base en el constructo «Aceleración con GPU y programación híbrida (MPI + OpenMP/CUDA)», busca artículos desde 2022, con DOI, que combinen MPI con OpenMP o CUDA para acelerar procesamiento o clasificación de imágenes y reporten aceleración o eficiencia.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `hybrid MPI OpenMP CUDA GPU acceleration` | ScienceDirect (10.1016) | 57.779 | 8 |
| `hybrid MPI OpenMP CUDA GPU acceleration` | todas las editoriales | 231.271 | 8 |
| `GPU parallel computing deep learning image processing` | ScienceDirect (10.1016) | 247.304 | 8 |
| `GPU parallel computing deep learning image processing` | todas las editoriales | 1.441.774 | 8 |

Referencias incluidas:

- Scalable communication for high-order stencil computations using CUDA-aware MPI (2022). https://doi.org/10.1016/j.parco.2022.102904
- A hybrid CUDA, OpenMP, and MPI parallel TCA-based domain adaptation for classification of very high-resolution remote sensing images (2023). https://doi.org/10.1007/s11227-022-04961-y
- A parallel numerical algorithm by combining MPI and OpenMP programming models with applications in gravity field recovery (2023). https://doi.org/10.3389/feart.2023.1080879

### C5. Infraestructura de clúster y red LAN para MPI

**Prompt:** Con base en el constructo «Infraestructura de clúster y red LAN para MPI», busca artículos desde 2022, con DOI, sobre la instalación y configuración de entornos MPI en clústeres de bajo costo o en red local (por ejemplo, Raspberry Pi) y sobre herramientas para usar MPI desde Python, con fines de investigación o enseñanza.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `cluster computing MPI containers deployment` | ScienceDirect (10.1016) | 26.789 | 8 |
| `cluster computing MPI containers deployment` | todas las editoriales | 199.259 | 8 |
| `low-cost cluster parallel computing education` | ScienceDirect (10.1016) | 159.472 | 8 |
| `low-cost cluster parallel computing education` | todas las editoriales | 1.537.483 | 8 |
| `Raspberry Pi cluster MPI parallel computing` | ScienceDirect (10.1016) | 33.434 | 8 |
| `Raspberry Pi cluster MPI parallel computing` | todas las editoriales | 232.108 | 8 |
| `teaching parallel programming MPI cluster students` | ScienceDirect (10.1016) | 40.350 | 8 |
| `teaching parallel programming MPI cluster students` | todas las editoriales | 704.730 | 8 |

Referencias incluidas:

- Numba-MPI v1.0: Enabling MPI communication within Numba/LLVM JIT-compiled Python code (2024). https://doi.org/10.1016/j.softx.2024.101897
- Hands-on parallel & distributed computing with Raspberry Pi devices and clusters (2025). https://doi.org/10.1016/j.jpdc.2024.104996
- TopADDPi: An Affordable and Sustainable Raspberry Pi Cluster for Parallel-Computing Topology Optimization (2025). https://doi.org/10.3390/pr13030633

### C6. Visión por computador con CNN para enfermedades y plagas de cultivos

**Prompt:** Con base en el constructo «Visión por computador con CNN para enfermedades y plagas de cultivos», busca artículos desde 2022, con DOI, que clasifiquen o detecten enfermedades en hojas (en especial de café y roya) con redes convolucionales y aprendizaje por transferencia, y que reporten exactitud o F1.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `coffee leaf disease detection deep learning` | ScienceDirect (10.1016) | 360.262 | 8 |
| `coffee leaf disease detection deep learning` | todas las editoriales | 1.955.184 | 8 |
| `plant disease classification convolutional neural network transfer learning` | ScienceDirect (10.1016) | 433.943 | 8 |
| `plant disease classification convolutional neural network transfer learning` | todas las editoriales | 2.335.381 | 8 |
| `coffee leaf rust detection deep learning images` | ScienceDirect (10.1016) | 256.299 | 8 |
| `coffee leaf rust detection deep learning images` | todas las editoriales | 1.462.209 | 8 |

Referencias incluidas:

- Transfer Learning for Multi-Crop Leaf Disease Image Classification using Convolutional Neural Network VGG (2022). https://doi.org/10.1016/j.aiia.2021.12.002
- CoLeaf-DB: Peruvian coffee leaf images dataset for coffee leaf nutritional deficiencies detection and classification (2023). https://doi.org/10.1016/j.dib.2023.109226
- Coffee Leaf Rust Disease Detection and Implementation of an Edge Device for Pruning Infected Leaves via Deep Learning Algorithms (2024). https://doi.org/10.3390/s24248018
- Early Detection of Coffee Leaf Rust Caused by Hemileia vastatrix Using Multispectral Images (2022). https://doi.org/10.3390/agronomy12122911
- Influence of Hyperparameters in Deep Learning Models for Coffee Rust Detection (2023). https://doi.org/10.3390/app13074565

### C7. Inferencia eficiente en el borde (dispositivos móviles)

**Prompt:** Con base en el constructo «Inferencia eficiente en el borde (dispositivos móviles)», busca artículos desde 2022, con DOI, sobre modelos ligeros de detección de enfermedades de plantas ejecutados en teléfonos o dispositivos de borde, que reporten latencia, tamaño del modelo o consumo de recursos.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `edge computing deep learning inference mobile agriculture` | ScienceDirect (10.1016) | 206.694 | 8 |
| `edge computing deep learning inference mobile agriculture` | todas las editoriales | 1.372.146 | 8 |
| `lightweight CNN mobile plant disease detection` | ScienceDirect (10.1016) | 260.431 | 8 |
| `lightweight CNN mobile plant disease detection` | todas las editoriales | 1.329.842 | 8 |

Referencias incluidas:

- RTR_Lite_MobileNetV2: A lightweight and efficient model for plant disease detection and classification (2025). https://doi.org/10.1016/j.cpb.2025.100459
- Leveraging Deep Learning for Real-Time Coffee Leaf Disease Identification (2025). https://doi.org/10.3390/agriengineering7010013
- Grow-light smart monitoring system leveraging lightweight deep learning for plant disease classification (2024). https://doi.org/10.1016/j.aiia.2024.03.003

### C8. Aprendizaje federado y sistemas distribuidos en agricultura

**Prompt:** Con base en el constructo «Aprendizaje federado y sistemas distribuidos en agricultura», busca artículos desde 2022, con DOI, sobre entrenamiento colaborativo de modelos entre varias fincas o nodos y sobre sistemas inteligentes de visión en agricultura de precisión.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `federated learning agriculture plant disease` | ScienceDirect (10.1016) | 299.293 | 8 |
| `federated learning agriculture plant disease` | todas las editoriales | 1.824.792 | 8 |
| `distributed artificial intelligence smart farming` | ScienceDirect (10.1016) | 77.677 | 8 |
| `distributed artificial intelligence smart farming` | todas las editoriales | 562.367 | 8 |

Referencias incluidas:

- AGRIFOLD: AGRIculture Federated learning for Optimized Leaf disease Detection (2025). https://doi.org/10.1016/j.eswa.2025.128371
- Computer vision in smart agriculture and precision farming: Techniques and applications (2024). https://doi.org/10.1016/j.aiia.2024.06.004

## 3. Criterios de selección

**Inclusión:** artículo de revista; publicado desde 2022; DOI que resuelve en Crossref; resumen recuperable (Crossref, Semantic Scholar u OpenAlex); relación directa con un constructo; preferencia por ScienceDirect.

**Exclusión:** ruido semántico de la búsqueda (por ejemplo, *message passing* en redes de grafos o *point cloud overlap*); fecha anterior a 2022 o posterior a la de la búsqueda; sin resumen recuperable; redundancia con otro trabajo ya incluido del mismo constructo; fuera del alcance de clasificación de imágenes o de MPI; presencia previa en la biblioteca de Zotero del usuario (no hubo coincidencias).

## 4. Flujo de selección

| Etapa | Registros |
|---|---:|
| Búsquedas ejecutadas (cadenas × filtros) | 38 |
| Registros revisados (8 por búsqueda) | 304 |
| Registros únicos | 243 |
| Preseleccionados por título, revista y año, con verificación de DOI | 58 |
| Excluidos por no tener resumen recuperable | 22 |
| Excluidos por redundancia o alcance | 8 |
| **Incluidos** | **28** |

De los 28 incluidos, 16 son de ScienceDirect (Elsevier). De los 22 excluidos por no tener resumen, 19 son de ScienceDirect: esa editorial bloquea la lectura automática de sus páginas y no comparte sus resúmenes con las APIs abiertas. Se reemplazaron por otros artículos del mismo constructo.

Motivos de los excluidos por redundancia o alcance:

- https://doi.org/10.1016/j.procs.2022.12.041: Mismo grupo y caso de estudio que Patil y Chickerur (2023); se conservó el más reciente.
- https://doi.org/10.1371/journal.pone.0293338: Redundante con la encuesta de autoparalelismo y con Maruf et al. (2024).
- https://doi.org/10.1134/s1995080223080218: Resumen breve y centrado en una red de interconexión específica (Angara).
- https://doi.org/10.1016/j.ecoinf.2024.102925: Redundante con Paymode y Malode (2022) y sin relación con café.
- https://doi.org/10.1016/j.atech.2024.100526: Trata segmentación semántica, fuera del alcance de clasificación de BioCafe.
- https://doi.org/10.7717/peerj-cs.2406: Redundante con los otros cuatro trabajos sobre café ya incluidos.
- https://doi.org/10.1186/s13007-025-01386-5: Redundante con Duhan et al. (2025) en modelos móviles; cultivo distinto (maíz).
- https://doi.org/10.3390/agriculture16090918: Redundante con AGRIFOLD (2025) en aprendizaje federado.

## 5. Cómo repetir el proceso

```bash
python3 herramientas/buscar_crossref.py datos/constructos.json datos/busqueda_crossref.json 8
python3 herramientas/verificar_referencias.py datos/seleccion.json datos/referencias.json
python3 herramientas/limpiar_resumenes.py datos/referencias.json
python3 herramientas/generar_semilla.py datos .
python3 herramientas/generar_md_prompts.py datos 01_Constructos_y_prompts.md
```

Crossref ordena por relevancia y su índice cambia con el tiempo; repetir la búsqueda otro día puede dar totales y órdenes algo distintos.
