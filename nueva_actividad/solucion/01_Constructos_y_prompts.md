# Constructos y prompts de búsqueda

Revisión sistemática descriptiva: *Detección temprana de plagas y enfermedades del café con sistemas inteligentes y computación paralela y distribuida*.

Fecha de las búsquedas: 2026-10-27. Base consultada: Crossref REST API (api.crossref.org), que indexa ScienceDirect (Elsevier), IEEE, Springer, MDPI y otras editoriales. Todos los datos de este documento salen de los archivos de `datos/`; los scripts de `herramientas/` permiten repetir el proceso.

## 1. De dónde salen los constructos

El proyecto «Sistema de detección temprana de plagas y enfermedades en cultivos de café» (prototipo BioCafe) clasifica fotos de hojas de café (sana, roya, minador y arañita roja) con una red EfficientNet-B0 que se entrena en GPU y se ejecuta en el teléfono. Los constructos se derivaron del título y de los componentes del proyecto: el problema agrícola (C1, C2), el sistema inteligente (C3 a C5) y la computación paralela y distribuida que lo soporta (C6 a C8). La revisión trata sobre el proyecto, no sobre una tecnología en particular.

| ID | Constructo | Área | Definición operativa | Indicadores |
|---|---|---|---|---|
| C1 | Plagas y enfermedades foliares del café | Dominio del proyecto | Afectaciones de la hoja del cafeto que el sistema debe reconocer (roya, minador, arañita roja y otras) y su efecto en la producción. | tipo de afectación; síntomas visibles; pérdidas reportadas; región |
| C2 | Detección temprana y diagnóstico automatizado | Sistemas Inteligentes | Identificación de la afectación en sus primeras etapas, incluso antes de los síntomas visibles, mediante sensores, imágenes o modelos automáticos. | días tras la infección; tipo de sensor; exactitud de la detección |
| C3 | Conjuntos de datos de imágenes de hojas de café | Sistemas Inteligentes | Colecciones de fotos de hojas de café etiquetadas por afectación, que sirven para entrenar y evaluar los modelos. | número de imágenes; clases; condiciones de captura; licencia y disponibilidad |
| C4 | Clasificación con redes neuronales convolucionales y aprendizaje por transferencia | Sistemas Inteligentes | Modelos de aprendizaje profundo preentrenados y ajustados para clasificar la hoja según su afectación. | arquitectura; exactitud; F1; número de clases |
| C5 | Generalización y validación en condiciones de campo | Sistemas Inteligentes | Capacidad del modelo de mantener su desempeño con fotos de otras fincas, cámaras o condiciones de luz distintas a las del entrenamiento. | desempeño en conjunto externo; brecha laboratorio-campo; técnicas de aumento de datos |
| C6 | Entrenamiento acelerado con GPU y computación paralela | Computación Paralela y Distribuida | Uso de procesadores gráficos, paralelismo de datos y entrenamiento distribuido para reducir el tiempo de entrenamiento de los modelos. | tipo de paralelismo; aceleración; número de GPU o nodos |
| C7 | Inferencia en el dispositivo móvil y en el borde | Sistemas Inteligentes + Computación Paralela y Distribuida | Ejecución del modelo en el teléfono o en dispositivos de borde, sin conexión, con modelos ligeros o comprimidos. | latencia; tamaño del modelo; dispositivo; funcionamiento sin conexión |
| C8 | Sistemas distribuidos, IoT y aprendizaje federado en agricultura | Computación Paralela y Distribuida | Arquitecturas que reparten el cómputo y los datos entre fincas, dispositivos y la nube, incluido el entrenamiento colaborativo sin centralizar los datos. | arquitectura nube-borde; número de nodos o clientes; privacidad de los datos |

## 2. Prompts y cadenas de búsqueda por constructo

Cada prompt expresa el pedido de referencias que nace del constructo; las cadenas son su traducción a la consulta bibliográfica que se ejecutó. Cada cadena se lanzó dos veces: limitada a ScienceDirect (prefijo DOI 10.1016) y sin límite de editorial. Filtros comunes: artículos de revista (`type:journal-article`) publicados desde el 2022-01-01 (menos de 5 años).

### C1. Plagas y enfermedades foliares del café

**Prompt:** Con base en el constructo «Plagas y enfermedades foliares del café» del proyecto BioCafe, busca artículos de revista publicados desde 2022, con DOI y preferiblemente de ScienceDirect, que describan la roya, el minador u otras afectaciones de la hoja del café, sus síntomas y su impacto en la producción.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `coffee leaf rust Hemileia vastatrix impact management` | ScienceDirect (10.1016) | 250.618 | 10 |
| `coffee leaf rust Hemileia vastatrix impact management` | todas las editoriales | 1.792.534 | 10 |
| `coffee leaf miner pest damage` | ScienceDirect (10.1016) | 32.954 | 10 |
| `coffee leaf miner pest damage` | todas las editoriales | 164.913 | 10 |

Referencias incluidas:

- Coffee leaf rust and berry borer management in agroforestry systems: A systematic literature review (2024). https://doi.org/10.1016/j.atech.2024.100656
- Monitoring Coffee Leaf Rust (Hemileia vastatrix) on Commercial Coffee Farms in Hawaii: Early Insights from the First Year of Disease Incursion (2022). https://doi.org/10.3390/agronomy12051134
- Fungicide efficacy and duration of protection against coffee leaf rust (Hemileia vastatrix) on commercial coffee farms in Hawaii (2025). https://doi.org/10.1016/j.cropro.2025.107269
- Status of coffee leaf rust ( Hemileia vastatrix ) and its management in Ethiopia: a review (2022). https://doi.org/10.1080/03235408.2023.2168173
- The effects of thiamethoxam on coffee seedling morphophysiology and Neotropical leaf miner ( Leucoptera coffeella ) infestations (2022). https://doi.org/10.1002/ps.6889

### C2. Detección temprana y diagnóstico automatizado

**Prompt:** Con base en el constructo «Detección temprana y diagnóstico automatizado», busca artículos desde 2022, con DOI, que detecten enfermedades de cultivos en etapas tempranas o presintomáticas con imágenes, sensores o aprendizaje automático, en especial en café.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `early detection coffee leaf rust images` | ScienceDirect (10.1016) | 155.820 | 10 |
| `early detection coffee leaf rust images` | todas las editoriales | 794.600 | 10 |
| `early plant disease detection machine learning sensors` | ScienceDirect (10.1016) | 429.574 | 10 |
| `early plant disease detection machine learning sensors` | todas las editoriales | 2.410.826 | 10 |

Referencias incluidas:

- Early Detection of Coffee Leaf Rust Caused by Hemileia vastatrix Using Multispectral Images (2022). https://doi.org/10.3390/agronomy12122911
- Vegetation Indices Applied to Suborbital Multispectral Images of Healthy Coffee and Coffee Infested with Coffee Leaf Miner (2022). https://doi.org/10.3390/agriengineering4010021
- A comprehensive review on detection of plant disease using machine learning and deep learning approaches (2022). https://doi.org/10.1016/j.measen.2022.100441
- Machine learning-integrated plant biosensors for precision agriculture: A systematic review of stress detection, pathogen monitoring and smart crop management (2026). https://doi.org/10.1016/j.snr.2026.100502

### C3. Conjuntos de datos de imágenes de hojas de café

**Prompt:** Con base en el constructo «Conjuntos de datos de imágenes de hojas de café», busca artículos desde 2022, con DOI, que publiquen o analicen datasets de imágenes de hojas de café con enfermedades, plagas o deficiencias, preferiblemente en Data in Brief (ScienceDirect).

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `coffee leaf images dataset` | ScienceDirect (10.1016) | 27.431 | 10 |
| `coffee leaf images dataset` | todas las editoriales | 173.757 | 10 |
| `coffee disease image dataset Data in Brief` | ScienceDirect (10.1016) | 242.667 | 10 |
| `coffee disease image dataset Data in Brief` | todas las editoriales | 1.322.384 | 10 |

Referencias incluidas:

- Colombian coffee tree leaves multispectral images dataset (2025). https://doi.org/10.1016/j.dib.2025.111421
- CoLeaf-DB: Peruvian coffee leaf images dataset for coffee leaf nutritional deficiencies detection and classification (2023). https://doi.org/10.1016/j.dib.2023.109226

### C4. Clasificación con redes neuronales convolucionales y aprendizaje por transferencia

**Prompt:** Con base en el constructo «Clasificación con CNN y aprendizaje por transferencia», busca artículos desde 2022, con DOI, que clasifiquen enfermedades de hojas de café o de otros cultivos con redes convolucionales preentrenadas (EfficientNet, MobileNet, ResNet, VGG) y reporten exactitud o F1.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `coffee leaf disease classification deep learning` | ScienceDirect (10.1016) | 298.498 | 10 |
| `coffee leaf disease classification deep learning` | todas las editoriales | 1.728.434 | 10 |
| `plant leaf disease classification transfer learning EfficientNet` | ScienceDirect (10.1016) | 350.894 | 10 |
| `plant leaf disease classification transfer learning EfficientNet` | todas las editoriales | 1.971.545 | 10 |

Referencias incluidas:

- Coffee disease classification at the edge using deep learning (2023). https://doi.org/10.1016/j.atech.2023.100183
- Leveraging Deep Learning for Real-Time Coffee Leaf Disease Identification (2025). https://doi.org/10.3390/agriengineering7010013
- Influence of Hyperparameters in Deep Learning Models for Coffee Rust Detection (2023). https://doi.org/10.3390/app13074565
- Coffee-Net: Deep Mobile Patch Generation Network for Coffee Leaf Disease Classification (2025). https://doi.org/10.1109/jsen.2024.3498050
- Transfer Learning for Multi-Crop Leaf Disease Image Classification using Convolutional Neural Network VGG (2022). https://doi.org/10.1016/j.aiia.2021.12.002
- Coffee Leaf Rust Disease Detection and Implementation of an Edge Device for Pruning Infected Leaves via Deep Learning Algorithms (2024). https://doi.org/10.3390/s24248018

### C5. Generalización y validación en condiciones de campo

**Prompt:** Con base en el constructo «Generalización y validación en condiciones de campo», busca artículos desde 2022, con DOI, que evalúen modelos de enfermedades de plantas con imágenes de campo o de otras fuentes y analicen la caída de desempeño frente al laboratorio.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `plant disease detection field conditions generalization deep learning` | ScienceDirect (10.1016) | 459.210 | 10 |
| `plant disease detection field conditions generalization deep learning` | todas las editoriales | 2.490.349 | 10 |
| `domain shift plant disease images real field` | ScienceDirect (10.1016) | 266.586 | 10 |
| `domain shift plant disease images real field` | todas las editoriales | 1.361.646 | 10 |

Referencias incluidas:

- Toward Generalization of Deep Learning-Based Plant Disease Identification Under Controlled and Field Conditions (2023). https://doi.org/10.1109/access.2023.3240100
- From Laboratory to Field: Unsupervised Domain Adaptation for Plant Disease Recognition in the Wild (2023). https://doi.org/10.34133/plantphenomics.0038
- Bridging the Lab-to-Field gap in plant disease diagnosis through unsupervised domain adaptation enhanced by background recomposition (2026). https://doi.org/10.1016/j.ecoinf.2025.103579
- Innovative deep learning approach for cross-crop plant disease detection: A generalized method for identifying unhealthy leaves (2025). https://doi.org/10.1016/j.inpa.2024.03.002

### C6. Entrenamiento acelerado con GPU y computación paralela

**Prompt:** Con base en el constructo «Entrenamiento acelerado con GPU y computación paralela», busca artículos desde 2022, con DOI, que expliquen o midan el paralelismo de datos, de modelo o el uso de GPU para entrenar redes convolucionales de clasificación de imágenes.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `distributed deep learning training data parallelism GPU` | ScienceDirect (10.1016) | 262.499 | 10 |
| `distributed deep learning training data parallelism GPU` | todas las editoriales | 1.679.050 | 10 |
| `parallel training convolutional neural networks GPU cluster` | ScienceDirect (10.1016) | 107.454 | 10 |
| `parallel training convolutional neural networks GPU cluster` | todas las editoriales | 605.614 | 10 |

Referencias incluidas:

- Study of Data and Model parallelism in Distributed Deep learning for Diabetic retinopathy classification (2023). https://doi.org/10.1016/j.procs.2023.01.201
- A snapshot of parallelism in distributed deep learning training (2024). https://doi.org/10.29375/25392115.5054
- Analyzing the impact of the MPI allreduce in distributed training of convolutional neural networks (2023). https://doi.org/10.1007/s00607-021-01029-2
- A Survey on Auto-Parallelism of Large-Scale Deep Learning Training (2023). https://doi.org/10.1109/tpds.2023.3281931

### C7. Inferencia en el dispositivo móvil y en el borde

**Prompt:** Con base en el constructo «Inferencia en el dispositivo móvil y en el borde», busca artículos desde 2022, con DOI, sobre aplicaciones móviles o dispositivos de borde que detecten enfermedades de plantas con modelos ligeros, y que reporten latencia, tamaño o consumo.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `mobile application plant disease detection smartphone deep learning` | ScienceDirect (10.1016) | 451.201 | 10 |
| `mobile application plant disease detection smartphone deep learning` | todas las editoriales | 2.520.138 | 10 |
| `lightweight model edge device plant disease detection` | ScienceDirect (10.1016) | 400.344 | 10 |
| `lightweight model edge device plant disease detection` | todas las editoriales | 2.057.495 | 10 |

Referencias incluidas:

- RTR_Lite_MobileNetV2: A lightweight and efficient model for plant disease detection and classification (2025). https://doi.org/10.1016/j.cpb.2025.100459
- Application of smartphone-image processing and transfer learning for rice disease and nutrient deficiency detection (2023). https://doi.org/10.1016/j.atech.2023.100195
- Plant disease detection model for edge computing devices (2023). https://doi.org/10.3389/fpls.2023.1308528
- Deep Learning Based Mobile Application for Automated Plant Disease Detection (2025). https://doi.org/10.1109/access.2025.3581099

### C8. Sistemas distribuidos, IoT y aprendizaje federado en agricultura

**Prompt:** Con base en el constructo «Sistemas distribuidos, IoT y aprendizaje federado en agricultura», busca artículos desde 2022, con DOI, sobre aprendizaje federado, computación en la nube y en el borde o IoT aplicados a la detección de enfermedades de cultivos.

| Cadena de búsqueda | Filtro de editorial | Resultados totales | Mostrados |
|---|---|---:|---:|
| `federated learning plant disease detection agriculture` | ScienceDirect (10.1016) | 378.035 | 10 |
| `federated learning plant disease detection agriculture` | todas las editoriales | 2.152.141 | 10 |
| `IoT edge cloud computing crop disease monitoring` | ScienceDirect (10.1016) | 192.948 | 10 |
| `IoT edge cloud computing crop disease monitoring` | todas las editoriales | 1.071.403 | 10 |

Referencias incluidas:

- AGRIFOLD: AGRIculture Federated learning for Optimized Leaf disease Detection (2025). https://doi.org/10.1016/j.eswa.2025.128371
- Computer vision in smart agriculture and precision farming: Techniques and applications (2024). https://doi.org/10.1016/j.aiia.2024.06.004
- Cocoa Companion: Deep Learning-Based Smartphone Application for Cocoa Disease Detection (2022). https://doi.org/10.1016/j.procs.2022.07.013

## 3. Criterios de selección

**Inclusión:** artículo de revista; publicado desde 2022; DOI que resuelve en Crossref; resumen recuperable (Crossref, Semantic Scholar u OpenAlex); relación directa con un constructo; preferencia por ScienceDirect.

**Exclusión:** ruido semántico de la búsqueda (por ejemplo, *message passing* en redes de grafos o *point cloud overlap*); fecha anterior a 2022 o posterior a la de la búsqueda; sin resumen recuperable; redundancia con otro trabajo ya incluido del mismo constructo; fuera del alcance de clasificación de imágenes o de MPI; presencia previa en la biblioteca de Zotero del usuario (no hubo coincidencias).

## 4. Flujo de selección

| Etapa | Registros |
|---|---:|
| Búsquedas ejecutadas (cadenas × filtros) | 32 |
| Registros revisados (10 por búsqueda) | 320 |
| Registros únicos | 236 |
| Añadidos de la primera búsqueda (versión MPI, ver `datos/v1_mpi/`) | 4 |
| Preseleccionados por título, revista y año, con verificación de DOI | 45 |
| Excluidos por no tener resumen recuperable | 10 |
| Excluidos por redundancia o alcance | 3 |
| **Incluidos** | **32** |

De los 32 incluidos, 16 son de ScienceDirect (Elsevier). De los 10 excluidos por no tener resumen, 7 son de ScienceDirect: esa editorial bloquea la lectura automática de sus páginas y no comparte sus resúmenes con las APIs abiertas. Cada constructo quedó cubierto con otros artículos que sí tienen resumen.

Motivos de los excluidos por redundancia o alcance:

- https://doi.org/10.1016/j.heliyon.2022.e11892: Epidemiología de la roya en sistemas agroforestales de Etiopía; redundante con las otras cuatro referencias del dominio.
- https://doi.org/10.1016/j.baae.2023.11.006: Control biológico del minador en laboratorio; se conservó un trabajo del minador con daño y manejo en cultivo (Leite et al., 2022).
- https://doi.org/10.34133/plantphenomics.0201: Estimación de severidad de roya del trigo por segmentación; redundante con las aplicaciones móviles incluidas y fuera del alcance de clasificación.

## 5. Cómo repetir el proceso

```bash
python3 herramientas/buscar_crossref.py datos/constructos.json datos/busqueda_crossref.json 8
python3 herramientas/verificar_referencias.py datos/preseleccion.json datos/preseleccion_verificada.json
python3 herramientas/limpiar_resumenes.py datos/referencias.json
python3 herramientas/generar_semilla.py datos .
python3 herramientas/generar_md_prompts.py datos 01_Constructos_y_prompts.md
```

Crossref ordena por relevancia y su índice cambia con el tiempo; repetir la búsqueda otro día puede dar totales y órdenes algo distintos.
