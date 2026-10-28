"""Text of the IEEE article and of the traceability document.

Citations use [@key] or [@key1; @key2] with the keys produced by generar_semilla.key();
generar_documentos.py turns them into IEEE numbers in order of first appearance.
Every figure quoted from a study comes from its abstract (datos/referencias.json);
figures about BioCafe come from the project repository (docs/resultados.md).
"""

TITULO = ("Computación paralela con MPI y sistemas inteligentes para la detección temprana de "
          "enfermedades en hojas de café: una revisión sistemática descriptiva")
TITLE_EN = ("Parallel computing with MPI and intelligent systems for the early detection of coffee leaf "
            "diseases: a descriptive systematic review")
AUTORES = ["Heyley Yurani Parada Parada", "Lisbeth Gissel Cordero Tovar"]
IDENTIFICACION = {"Heyley Yurani Parada Parada": "1093887319", "Lisbeth Gissel Cordero Tovar": "1093293375"}

def autores_con_id():
    return [f"{n} (identificación {IDENTIFICACION[n]})" for n in AUTORES]
AFILIACION = ["Programa de Ingeniería de Sistemas, Facultad de Ingenierías y Arquitectura",
              "Universidad de Pamplona, Villa del Rosario, Norte de Santander, Colombia"]

RESUMEN = (
    "La detección temprana de enfermedades del café con visión por computador exige entrenar redes neuronales "
    "convolucionales con miles de imágenes, una tarea costosa que la computación paralela y distribuida puede acelerar. "
    "Este artículo presenta una revisión sistemática descriptiva sobre la Interfaz de Paso de Mensajes (MPI) y los sistemas "
    "inteligentes aplicables a BioCafe, una aplicación móvil que clasifica hojas de café en sana, roya, minador y arañita roja. "
    "A partir de ocho constructos se formularon prompts y cadenas de búsqueda que se ejecutaron en Crossref el 27 de octubre "
    "de 2026, limitadas a artículos de revista publicados desde 2022 y con prioridad para ScienceDirect. De 243 registros "
    "únicos se incluyeron 28 artículos con DOI verificado, 16 de ellos de ScienceDirect. La literatura muestra que elegir "
    "bien la biblioteca MPI y el algoritmo de Allreduce acelera hasta 2,8 veces el entrenamiento distribuido de redes "
    "convolucionales; que la programación híbrida MPI + OpenMP/CUDA es la vía habitual para usar varias GPU; que los "
    "clústeres de Raspberry Pi permiten enseñar e investigar con MPI a bajo costo, y que los modelos ligeros y el aprendizaje "
    "federado acercan el diagnóstico al cultivo. Se concluye que MPI aporta a BioCafe en el reentrenamiento con más datos y "
    "en un laboratorio de clúster, mientras que la inferencia ya se resuelve en el teléfono. No se hallaron trabajos que "
    "apliquen MPI a enfermedades del café.")

ABSTRACT = (
    "Early detection of coffee diseases through computer vision requires training convolutional neural networks on "
    "thousands of images, a costly task that parallel and distributed computing can speed up. This paper presents a "
    "descriptive systematic review of the Message Passing Interface (MPI) and of the intelligent systems applicable to "
    "BioCafe, a mobile application that classifies coffee leaves as healthy, rust, leaf miner or red spider mite. Eight "
    "constructs were turned into prompts and search strings that were run on Crossref on October 27, 2026, restricted to "
    "journal articles published since 2022 and giving priority to ScienceDirect. Out of 243 unique records, 28 articles "
    "with a verified DOI were included, 16 of them from ScienceDirect. The literature shows that choosing the right MPI "
    "library and Allreduce algorithm speeds up distributed training of convolutional networks by up to 2.8 times; that "
    "hybrid MPI + OpenMP/CUDA programming is the usual way to exploit several GPUs; that Raspberry Pi clusters make it "
    "possible to teach and research MPI at low cost; and that lightweight models and federated learning bring diagnosis "
    "closer to the field. MPI benefits BioCafe in retraining with more data and in a cluster laboratory, while inference "
    "is already solved on the phone. No study applying MPI to coffee diseases was found.")

PALABRAS_CLAVE = ("MPI, computación paralela y distribuida, entrenamiento distribuido, Allreduce, sistemas inteligentes, "
                  "redes neuronales convolucionales, roya del café, computación en el borde.")
INDEX_TERMS = ("MPI, parallel and distributed computing, distributed training, Allreduce, intelligent systems, "
               "convolutional neural networks, coffee leaf rust, edge computing.")

# Each section: (title, [blocks]); a block is a paragraph string, ("sub", "A. ...") a subsection,
# ("tabla", id) a table defined in generar_documentos.py, or ("figura", id) a figure.
SECCIONES = [
    ("Introducción", [
        "La roya del café, causada por Hemileia vastatrix, es el patógeno más importante de este cultivo en el mundo, y los "
        "métodos convencionales de muestreo en campo han resultado poco prácticos para detectarla a tiempo [@soares2022early]. "
        "La enfermedad reduce la productividad y obliga a decidir qué hojas podar o dónde aplicar fungicida [@araaf2024coffee]. "
        "Identificar las enfermedades en sus primeras etapas es determinante para sostener los rendimientos y la seguridad "
        "alimentaria [@duhan2025lite].",
        "Las redes neuronales convolucionales (CNN) con aprendizaje por transferencia son hoy la técnica dominante para "
        "clasificar enfermedades en imágenes de hojas [@paymode2022transfer], y en café la arquitectura base elegida es el "
        "hiperparámetro que más influye en el resultado [@chavarro2023influence]. Entrenarlas, sin embargo, es costoso: a "
        "medida que crecen los modelos y los datos se vuelve necesario distribuir el entrenamiento entre varios dispositivos "
        "o nodos [@liang2023survey; @romerosandi2024snapshot]. Aquí entran los fundamentos de la computación paralela y "
        "distribuida. La Interfaz de Paso de Mensajes (MPI) es el estándar de facto para programar aplicaciones paralelas en "
        "memoria distribuida [@hunold2026tuned; @utrera2026optimizing], y los paquetes de entrenamiento distribuido más usados "
        "dependen del rendimiento de su operación colectiva Allreduce [@nuriyev2024suara].",
        "BioCafe es el prototipo del proyecto «Sistema de detección temprana de plagas y enfermedades en cultivos de café». "
        "Clasifica una foto de una hoja en cuatro clases (sana, roya, minador y arañita roja) con una red EfficientNet-B0 "
        "entrenada en una sola GPU de Google Colab y ejecutada en el teléfono, sin conexión. En el repositorio del proyecto, "
        "el modelo alcanza una exactitud de 0,94 en la prueba interna y de 0,81 en un conjunto externo, y tarda 48 ms por "
        "imagen en un teléfono Android. El entrenamiento, por tanto, ya funciona en una GPU, y la inferencia ya ocurre en "
        "el dispositivo. La pregunta práctica es en qué parte del sistema aporta MPI y qué dice la literatura reciente sobre ello.",
        "El objetivo de esta revisión es describir el estado del conocimiento publicado desde 2022 sobre MPI y los sistemas "
        "inteligentes relacionados con la detección de enfermedades en hojas, y relacionarlo con BioCafe. Se plantean cuatro "
        "preguntas descriptivas: (PR1) ¿qué mecanismos de MPI, punto a punto y colectivos, se estudian para mejorar el "
        "rendimiento?; (PR2) ¿qué estrategias de entrenamiento distribuido y de programación híbrida se reportan para redes "
        "profundas?; (PR3) ¿qué infraestructura de clúster de bajo costo permite usar MPI fuera de un supercomputador?, y "
        "(PR4) ¿qué avances recientes hay en la detección de enfermedades de cultivos con CNN, en el borde y de forma federada? "
        "PR1 se responde con los constructos C1 y C2; PR2, con C3 y C4; PR3, con C5, y PR4, con C6 a C8. "
        "La sección II describe el método; la sección III presenta y discute los resultados por constructo, y la sección IV "
        "resume las conclusiones.",
    ]),
    ("Materiales y métodos", [
        ("sub", "A. Tipo de revisión"),
        "Se realizó una revisión sistemática de tipo descriptivo: su propósito es poner al día al lector sobre lo que se sabe "
        "de un tema en evolución, no responder una pregunta causal ni combinar resultados con metaanálisis. Se siguieron las "
        "cuatro etapas de la guía del curso: definir los objetivos, buscar la bibliografía con una estrategia documentada, "
        "organizar la información y redactar el informe.",
        ("sub", "B. Constructos"),
        "Los constructos cruzan las unidades del curso de MPI (fundamentación, instalación sobre una red LAN y sobre un "
        "clúster, comunicación punto a punto y comunicación colectiva) con los componentes inteligentes de BioCafe. Se "
        "definieron ocho constructos, cada uno con una definición operativa e indicadores (Tabla I).",
        ("tabla", "constructos"),
        ("sub", "C. Estrategia de búsqueda"),
        "Para cada constructo se redactó un prompt que expresa el pedido de referencias y, a partir de él, dos o tres cadenas "
        "de búsqueda en inglés. Las cadenas se ejecutaron el 27 de octubre de 2026 en la API de Crossref, que indexa "
        "ScienceDirect, IEEE, Springer, MDPI y otras editoriales. Cada cadena se lanzó dos veces, una limitada al prefijo DOI "
        "de Elsevier (10.1016, ScienceDirect) y otra sin límite de editorial, con dos filtros comunes: artículos de revista y "
        "fecha de publicación desde el 1 de enero de 2022. Se revisaron los ocho primeros resultados por relevancia de cada "
        "una de las 38 búsquedas. Los prompts, las cadenas exactas, los totales de resultados y los scripts que repiten el "
        "proceso quedaron documentados en el archivo de constructos y prompts que acompaña este artículo.",
        ("sub", "D. Criterios de selección"),
        "Se incluyeron artículos de revista publicados desde 2022, con DOI que resuelve en Crossref, con resumen recuperable "
        "y relacionados directamente con un constructo; se dio preferencia a ScienceDirect. Se excluyeron el ruido semántico "
        "de la búsqueda (por ejemplo, «message passing» en redes de grafos), los trabajos sin resumen recuperable, los "
        "redundantes con otro ya incluido del mismo constructo y los que estaban fuera del alcance de clasificación de "
        "imágenes o de MPI. También se verificó, mediante el servidor MCP de Zotero, que ninguno estuviera ya en la biblioteca "
        "de las autoras.",
        ("sub", "E. Verificación y extracción"),
        "Cada DOI se consultó en Crossref para confirmar su existencia, autores, revista y fecha. El resumen se tomó de "
        "Crossref, Semantic Scholar u OpenAlex. De cada artículo se extrajeron el objetivo, el método o la tecnología, el "
        "hallazgo principal con sus cifras y su relación con BioCafe. Las 28 referencias se cargaron en una colección de "
        "Zotero y se exportaron como archivo semilla (RIS y BibTeX) para poder importarlas en cualquier equipo.",
        ("sub", "F. Flujo de selección"),
        "Las 38 búsquedas devolvieron 304 registros revisados, 243 de ellos únicos. Por título, revista y año se "
        "preseleccionaron 58, a los que se les verificó el DOI. Se excluyeron 22 por no tener resumen recuperable (19 de "
        "ScienceDirect, editorial que no comparte sus resúmenes con las APIs abiertas) y 8 por redundancia o alcance, y "
        "quedaron 28 artículos incluidos (Fig. 1).",
        ("figura", "flujo"),
    ]),
    ("Resultados y discusión", [
        ("sub", "A. Panorama de los estudios incluidos"),
        "De los 28 artículos, 16 (57 %) son de ScienceDirect, 6 de MDPI, 2 de IEEE, 2 de Springer, 1 de Frontiers y 1 de la "
        "Revista Colombiana de Computación. Todos fueron publicados entre 2022 y 2026. Dieciocho artículos "
        "corresponden a Fundamentos de Computación Paralela y Distribuida (C1 a C5) y diez a Sistemas Inteligentes (C6 a C8), "
        "lo que responde al énfasis de la actividad en MPI sin perder de vista el problema agrícola del proyecto. La Tabla II "
        "reúne los hallazgos cuantitativos más relevantes para BioCafe.",
        ("tabla", "hallazgos"),
        ("sub", "B. Fundamentos de MPI y su rendimiento (C1)"),
        "Tres trabajos coinciden en que el rendimiento de una aplicación MPI depende de parámetros que el programador debe "
        "ajustar: número de procesos, granularidad, algoritmo colectivo, topología virtual y ubicación de los procesos. "
        "Cornebize y Legrand emulan una aplicación MPI en un solo servidor y predicen el rendimiento del benchmark HPL a escala "
        "de supercomputador con un error de pocos puntos porcentuales, lo que permite ajustar parámetros sin ocupar el clúster "
        "[@cornebize2022simulation]. Hunold et al. proponen una herramienta que verifica si una biblioteca MPI cumple pautas "
        "de rendimiento, como que una operación colectiva especializada no sea más lenta que su emulación con operaciones más "
        "simples [@hunold2026tuned]. Zhong et al. muestran que vectorizar las operaciones de reducción con instrucciones AVX y "
        "SVE reduce el tiempo de las reducciones colectivas en procesadores Intel, AMD y Arm [@zhong2022using]. Para el curso "
        "y para BioCafe, la lección es que instalar MPI no basta: hay que medir y ajustar.",
        ("sub", "C. Comunicación punto a punto y colectiva (C2)"),
        "En la comunicación punto a punto, Thune et al. modelan el costo de cada proceso cuando muchos pares compiten por el "
        "ancho de banda; con 8192 procesos en 64 nodos su modelo explica el costo real con una precisión del 84 % "
        "[@thune2023detailed]. Zheng y Wu revisan las primitivas no bloqueantes de MPI, que permiten solapar comunicación y "
        "cómputo para que los núcleos no esperen mientras llegan los datos [@zheng2025towards].",
        "En la comunicación colectiva, Allreduce es la operación central del entrenamiento distribuido con descenso de "
        "gradiente síncrono, porque suma los gradientes de todos los procesos en cada paso. SUARA, un metaalgoritmo que divide "
        "los procesos en subconjuntos y elige el mejor algoritmo para cada uno, más que duplica la velocidad del Allreduce de Open MPI "
        "en 1024 nodos y mejora en 9 % el entrenamiento de ResNet-50 sobre ImageNet [@nuriyev2024suara]. Utrera y Bull "
        "aprovechan la memoria compartida de MPI-3 dentro de cada nodo para Allreduce y Bcast, con menores tiempos para "
        "mensajes medianos y grandes [@utrera2026optimizing]. El resultado más cercano a BioCafe es el de Castelló et al.: en "
        "un clúster de pocos nodos que entrena CNN con TensorFlow y Horovod, elegir la biblioteca MPI (MPICH, Open MPI o Intel "
        "MPI) y la implementación de Allreduce acelera el entrenamiento 1,2 veces frente al algoritmo por defecto y hasta 2,8 "
        "veces entre bibliotecas [@castello2023analyzing].",
        ("sub", "D. Entrenamiento distribuido de redes profundas (C3)"),
        "Los estudios distinguen el paralelismo de datos, en el que cada proceso entrena una copia del modelo con una parte de "
        "los datos; el paralelismo de modelo, en el que el modelo se reparte entre dispositivos, y el paralelismo en tubería, "
        "que encadena las partes del modelo. Patil y Chickerur compararon los dos primeros para clasificar retinopatía "
        "diabética con Mesh-TensorFlow: el paralelismo de modelo logró 62,13 % de exactitud de validación frente a 55,72 % y "
        "una aceleración de 1,38 veces [@patil2023study]. Maruf et al. combinan paralelismo de datos, de modelo y en tubería "
        "para sistemas embebidos y reducen cerca de 44,87 % el tiempo de entrenamiento frente a AlexNet "
        "[@maruf2024optimizing]. Dos revisiones completan el panorama: la de autoparalelismo, que busca automáticamente la "
        "mejor combinación según el costo de comunicación y de memoria [@liang2023survey], y la publicada en la Revista "
        "Colombiana de Computación, que repasa las estrategias de tubería, híbridas y de mezcla de expertos e incluye "
        "experimentos con paralelismo de datos y de modelo [@romerosandi2024snapshot]. Para un modelo del tamaño de "
        "EfficientNet-B0, que cabe completo en una GPU, el paralelismo de datos con Allreduce es la opción natural.",
        ("sub", "E. Aceleración con GPU y programación híbrida (C4)"),
        "La programación híbrida usa MPI entre nodos, OpenMP entre hilos de un mismo nodo y CUDA dentro de la GPU. Pekkilä et "
        "al. implementan la comunicación con MPI compatible con CUDA, que mueve datos directamente entre GPU, y escalan de 1 a "
        "64 GPU con 50 % a 87 % de la eficiencia esperada; frente a un solucionador en CPU multinúcleo obtienen entre 20 y 60 "
        "veces más velocidad y entre 9 y 12 veces más eficiencia energética [@pekkila2022scalable]. Garea et al. paralelizan "
        "con MPI, OpenMP y GPU una técnica de clasificación de imágenes multiespectrales de muy alta resolución y obtienen "
        "aceleraciones altas frente a la versión secuencial, lo que muestra que el esquema híbrido sirve también para "
        "clasificar imágenes [@garea2023hybrid]. Lu et al. combinan MPI y OpenMP en un clúster de 108 núcleos y escalan la "
        "inversión de matrices hasta 100 núcleos [@lu2023parallel].",
        ("sub", "F. Infraestructura de clúster y red LAN (C5)"),
        "Las unidades del curso sobre instalación de MPI en una red LAN y en un clúster encuentran apoyo directo en tres "
        "trabajos. Shoop et al. publican módulos gratuitos y una imagen de disco que convierte varias Raspberry Pi en un "
        "clúster en minutos; su evaluación de varios años muestra que aumentan la confianza de estudiantes y docentes en los "
        "conceptos de computación paralela y distribuida [@shoop2025hands]. TopADDPi documenta cómo ensamblar y configurar un "
        "clúster de Raspberry Pi y lo compara con equipos convencionales en rendimiento, consumo energético y huella de carbono "
        "[@zhang2025topaddpi]. Del lado del software, numba-mpi permite llamar rutinas MPI (Send/Recv, Allreduce, Bcast, "
        "Scatter, Gather) desde código Python compilado con Numba [@derlatka2024numba]; como el código de entrenamiento de "
        "BioCafe está en Python, esta clase de puentes es la vía para incorporar MPI sin reescribirlo en C.",
        ("sub", "G. Sistemas inteligentes para enfermedades de cultivos (C6)"),
        "En detección de enfermedades, el aprendizaje por transferencia con VGG alcanzó 98,40 % de exactitud en uva y 95,71 % "
        "en tomate [@paymode2022transfer]. En café, Chavarro et al. compararon más de 800 modelos para clasificar roya y "
        "encontraron que la arquitectura base produce diferencias de hasta 70 % y el optimizador de hasta 20 % "
        "[@chavarro2023influence], lo que respalda que BioCafe haya elegido su arquitectura comparando alternativas. Araaf et "
        "al. detectaron roya con YOLOv8 (mAP de 73,2 %) y la ejecutaron en tiempo real en un dispositivo de borde integrado a "
        "una podadora [@araaf2024coffee]. Soares et al. distinguieron plántulas infectadas a los 15 días de la inoculación, "
        "antes de los síntomas visibles, con imágenes multiespectrales tomadas desde un dron y una máquina de vectores de "
        "soporte, con 80 % de exactitud [@soares2022early]. CoLeaf-DB aporta 1006 imágenes de hojas de café del Perú "
        "etiquetadas por deficiencia nutricional [@tuestamonteza2023coleaf], un recurso útil para ampliar las clases del "
        "proyecto.",
        ("sub", "H. Inferencia en el borde y aprendizaje federado (C7 y C8)"),
        "Los modelos ligeros llevan el diagnóstico al campo. RTR_Lite_MobileNet, una versión de MobileNetV2 con mecanismos de "
        "atención, logra 90,84 % de exactitud en un conjunto de café y se ejecuta en Raspberry Pi 4 y 5 con baja latencia y "
        "bajo consumo de memoria [@duhan2025lite]. CoffNet clasifica enfermedades de hojas de café con 97,88 % de "
        "exactitud a 125,93 imágenes por segundo [@adelaja2025leveraging], y una red sin preentrenamiento de solo 228 479 "
        "parámetros alcanza 96,75 % de exactitud en PlantVillage [@macdonald2024grow]. Estos resultados confirman la "
        "decisión de BioCafe de ejecutar el modelo en el teléfono. El aprendizaje federado es el paso distribuido siguiente: "
        "AGRIFOLD entrena una CNN ligera entre varios participantes sin compartir las imágenes, compara cinco métodos de "
        "agregación (el mejor fue SCAFFOLD) y aplica poda para llevar el modelo a dispositivos de borde "
        "[@piccialli2025agrifold]. Ghazal et al., por su parte, señalan los retos de desplegar modelos generales de visión "
        "en tiempo real en fincas autónomas [@ghazal2024computer].",
        ("sub", "I. Implicaciones para BioCafe"),
        "La literatura permite ubicar MPI con precisión dentro del proyecto. Primero, en el reentrenamiento: si se incorporan "
        "fotos de fincas de Norte de Santander, el paralelismo de datos con Horovod sobre MPI y un Allreduce bien elegido es "
        "la forma documentada de repartir el entrenamiento de EfficientNet-B0 entre varias GPU o nodos "
        "[@castello2023analyzing; @nuriyev2024suara]. Segundo, en la formación: un clúster de Raspberry Pi en red LAN "
        "permite practicar instalación, comunicación punto a punto y colectiva con bajo costo [@shoop2025hands; "
        "@zhang2025topaddpi], por ejemplo repartiendo con MPI la evaluación del modelo sobre miles de imágenes. Tercero, en la "
        "inferencia MPI no aporta: el teléfono ya clasifica una imagen en 48 ms y los trabajos de borde confirman que ese es "
        "el lugar adecuado [@duhan2025lite; @adelaja2025leveraging]. Finalmente, el aprendizaje federado ofrece una "
        "alternativa para mejorar el modelo con datos de varias fincas sin centralizar las fotos [@piccialli2025agrifold].",
        ("sub", "J. Vacíos y limitaciones"),
        "No se encontró ningún trabajo que aplique MPI al entrenamiento de modelos de enfermedades del café; los estudios de "
        "MPI se concentran en supercomputadores y en simulaciones científicas, y los de café en la exactitud del modelo. Esta "
        "revisión tiene límites propios: usó una sola base (Crossref), revisó los ocho primeros resultados de cada búsqueda y "
        "excluyó 22 artículos cuyo resumen no estaba disponible en APIs abiertas, lo que redujo la proporción de ScienceDirect.",
    ]),
    ("Conclusiones", [
        "La revisión identificó 28 artículos recientes, con DOI verificado, que describen el estado del conocimiento sobre MPI "
        "y sistemas inteligentes aplicables a la detección de enfermedades del café. Respecto a PR1, el rendimiento de MPI "
        "depende de ajustar procesos, algoritmos colectivos y su implementación, y Allreduce es la operación crítica del "
        "entrenamiento distribuido. Respecto a PR2, el paralelismo de datos con Allreduce y la programación híbrida MPI + "
        "OpenMP/CUDA son las estrategias más reportadas, con aceleraciones de hasta 2,8 veces solo por elegir bien la "
        "biblioteca MPI. Respecto a PR3, los clústeres de Raspberry Pi en red local son una infraestructura viable y "
        "documentada para enseñar e investigar con MPI. Respecto a PR4, las CNN con aprendizaje por transferencia, los modelos "
        "ligeros en el borde y el aprendizaje federado dominan la detección de enfermedades de cultivos, con trabajos "
        "específicos sobre roya del café.",
        "Para BioCafe, MPI tiene sentido en el reentrenamiento con más datos y en un laboratorio de clúster, no en la "
        "inferencia, que ya se resuelve en el teléfono. Como trabajo futuro se propone medir en un clúster de bajo costo el "
        "tiempo de entrenamiento distribuido de EfficientNet-B0 con Horovod y distintas bibliotecas MPI, y explorar el "
        "aprendizaje federado entre fincas. El vacío más claro es la ausencia de estudios que unan MPI y enfermedades del "
        "café, un espacio en el que este proyecto puede aportar.",
    ]),
]

# Spanish summary of each study, used in the traceability document and the comparative table.
RESUMEN_ES = {
    "cornebize2022simulation": "Emula aplicaciones MPI en un solo servidor con modelos estadísticos de la plataforma y predice el rendimiento de HPL a escala de supercomputador con pocos puntos porcentuales de error.",
    "hunold2026tuned": "Presenta una herramienta que verifica si las operaciones colectivas de una biblioteca MPI cumplen pautas de rendimiento y evalúa ese cumplimiento en supercomputadores actuales.",
    "zhong2022using": "Implementa las reducciones predefinidas de MPI con instrucciones vectoriales AVX y SVE y reduce el tiempo de las reducciones colectivas en procesadores Intel, AMD y Arm.",
    "nuriyev2024suara": "Propone SUARA, un metaalgoritmo de Allreduce que divide los procesos en subconjuntos; más que duplica la velocidad del Allreduce de Open MPI en 1024 nodos y mejora 9 % el entrenamiento de ResNet-50.",
    "utrera2026optimizing": "Diseña versiones jerárquicas de MPI_Allreduce y MPI_Bcast que aprovechan la memoria compartida de MPI-3 dentro del nodo y la sobresuscripción de CPU, con menores tiempos para mensajes medianos y grandes.",
    "castello2023analyzing": "Analiza Allreduce en MPICH, Open MPI e Intel MPI para entrenar CNN con TensorFlow y Horovod; la elección adecuada acelera 1,2 veces frente al algoritmo por defecto y hasta 2,8 veces entre bibliotecas.",
    "zheng2025towards": "Revisa la comunicación no bloqueante de MPI y las técnicas para solapar comunicación y cómputo, con un estudio experimental preliminar del progreso asíncrono.",
    "thune2023detailed": "Modela la comunicación punto a punto de MPI considerando heterogeneidad y contención; con 8192 procesos en 64 nodos explica el costo con 84 % de precisión.",
    "patil2023study": "Compara paralelismo de datos y de modelo con Mesh-TensorFlow para clasificar retinopatía diabética; el de modelo logra 62,13 % de exactitud frente a 55,72 % y una aceleración de 1,38 veces.",
    "maruf2024optimizing": "Combina paralelismo de datos, de modelo y en tubería para entrenar redes en sistemas embebidos y reduce cerca de 44,87 % el tiempo de entrenamiento frente a AlexNet.",
    "liang2023survey": "Revisa el autoparalelismo en el entrenamiento de modelos grandes: esquemas de paralelismo, su costo de comunicación y memoria, y los métodos para buscar la mejor estrategia.",
    "romerosandi2024snapshot": "Panorama del paralelismo en el entrenamiento distribuido (tubería, híbrido, mezcla de expertos, autoparalelismo) con experimentos de paralelismo de datos y de modelo.",
    "pekkila2022scalable": "Usa MPI compatible con CUDA para comunicar GPU en simulaciones de esténcil; escala de 1 a 64 GPU con 50 % a 87 % de eficiencia y supera entre 20 y 60 veces a la CPU.",
    "garea2023hybrid": "Paraleliza con MPI, OpenMP y GPU una técnica de adaptación de dominio para clasificar imágenes multiespectrales de muy alta resolución, con aceleraciones altas frente a la versión secuencial.",
    "lu2023parallel": "Combina MPI y OpenMP en un clúster de 108 núcleos para resolver ecuaciones normales del campo gravitatorio y escala la inversión de matrices hasta 100 núcleos.",
    "derlatka2024numba": "Presenta numba-mpi, que expone rutinas MPI (Send/Recv, Allreduce, Bcast, Scatter, Gather) a código Python compilado con Numba, probado en Linux, macOS y Windows.",
    "shoop2025hands": "Ofrece módulos gratuitos y una imagen de disco para montar clústeres de Raspberry Pi en minutos y enseñar computación paralela y distribuida; aumenta la confianza de estudiantes y docentes.",
    "zhang2025topaddpi": "Documenta el ensamblaje y la configuración de un clúster de Raspberry Pi para cómputo paralelo y lo compara con equipos convencionales en rendimiento, energía y huella de carbono.",
    "paymode2022transfer": "Aplica aprendizaje por transferencia con VGG para clasificar enfermedades en hojas de uva y tomate, con 98,40 % y 95,71 % de exactitud.",
    "tuestamonteza2023coleaf": "Publica CoLeaf-DB, 1006 imágenes de hojas de café del Perú etiquetadas por agrónomos según deficiencias nutricionales, para entrenar modelos de aprendizaje profundo.",
    "araaf2024coffee": "Detecta roya del café con YOLOv5 y YOLOv8 sobre 2024 imágenes (mAP de 73,2 % con YOLOv8) y despliega el modelo en un dispositivo de borde integrado a una podadora.",
    "soares2022early": "Detecta roya en plántulas a los 15 días de la inoculación, antes de los síntomas, con imágenes multiespectrales desde un dron y SVM, con 80 % de exactitud.",
    "chavarro2023influence": "Compara más de 800 modelos de transferencia para clasificar roya del café; la arquitectura base causa diferencias de hasta 70 % y el optimizador de hasta 20 %.",
    "duhan2025lite": "Propone RTR_Lite_MobileNet, una MobileNetV2 con atención, con 90,84 % de exactitud en café y baja latencia y consumo de memoria en Raspberry Pi 4 y 5.",
    "adelaja2025leveraging": "Propone CoffNet para identificar enfermedades de hojas de café en tiempo real, con 97,88 % de exactitud y 125,93 imágenes por segundo.",
    "macdonald2024grow": "Diseña CNN ligeras sin preentrenamiento para un sistema de monitoreo en invernadero; la mejor tiene 228 479 parámetros y 96,75 % de exactitud en PlantVillage.",
    "piccialli2025agrifold": "Presenta AGRIFOLD, aprendizaje federado de una CNN ligera para hojas enfermas que preserva la privacidad; compara cinco métodos de agregación (el mejor fue SCAFFOLD) en 12 conjuntos de datos.",
    "ghazal2024computer": "Revisa las técnicas de visión por computador en la agricultura de precisión y los retos para desplegar modelos generales en tiempo real en fincas.",
}

# How each study relates to BioCafe, and its relevance (Alta/Media).
RELACION = {
    "cornebize2022simulation": ("Permite estimar el efecto de parámetros MPI antes de usar un clúster real, útil para planear el laboratorio.", "Media"),
    "hunold2026tuned": ("Recuerda verificar que las colectivas de la biblioteca MPI instalada rindan lo esperado antes de entrenar.", "Media"),
    "zhong2022using": ("Muestra que las reducciones (la base de Allreduce) dependen del hardware de la CPU del clúster.", "Media"),
    "nuriyev2024suara": ("Evidencia que optimizar Allreduce mejora directamente el entrenamiento de una CNN de clasificación de imágenes.", "Alta"),
    "utrera2026optimizing": ("Aplica a nodos con varios núcleos o varias GPU, donde la memoria compartida acelera las colectivas.", "Media"),
    "castello2023analyzing": ("Es el caso más cercano: CNN con TensorFlow y Horovod sobre MPI en un clúster pequeño, como el que usaría BioCafe.", "Alta"),
    "zheng2025towards": ("Sustenta el uso de Isend/Irecv para solapar la carga de imágenes con el cómputo en un reparto con MPI.", "Media"),
    "thune2023detailed": ("Explica por qué la comunicación punto a punto se degrada cuando muchos procesos compiten en la red LAN.", "Media"),
    "patil2023study": ("Compara estrategias de paralelismo en clasificación de imágenes médicas, un problema análogo al de las hojas.", "Alta"),
    "maruf2024optimizing": ("Muestra que el paralelismo también ayuda en hardware limitado, como el que tendría un laboratorio universitario.", "Media"),
    "liang2023survey": ("Ofrece el marco conceptual para elegir entre paralelismo de datos, de modelo o en tubería.", "Media"),
    "romerosandi2024snapshot": ("Fuente colombiana y didáctica sobre los tipos de paralelismo, con experimentos reproducibles.", "Alta"),
    "pekkila2022scalable": ("Muestra el beneficio de mover datos directamente entre GPU con MPI compatible con CUDA.", "Media"),
    "garea2023hybrid": ("Demuestra que el esquema híbrido MPI + OpenMP + GPU sirve para clasificar imágenes.", "Alta"),
    "lu2023parallel": ("Ejemplo didáctico de combinar MPI entre nodos y OpenMP dentro del nodo en un clúster universitario.", "Media"),
    "derlatka2024numba": ("Permite usar MPI desde Python, el lenguaje del pipeline de entrenamiento de BioCafe.", "Alta"),
    "shoop2025hands": ("Guía práctica para montar el clúster de Raspberry Pi de las unidades de LAN y clúster del curso.", "Alta"),
    "zhang2025topaddpi": ("Instrucciones de ensamblaje y datos de consumo para un clúster de bajo costo.", "Alta"),
    "paymode2022transfer": ("Respalda el aprendizaje por transferencia que usa BioCafe.", "Media"),
    "tuestamonteza2023coleaf": ("Conjunto de datos de café que podría ampliar las clases del proyecto (deficiencias nutricionales).", "Media"),
    "araaf2024coffee": ("Detección de roya del café en un dispositivo de borde, comparable con la app móvil de BioCafe.", "Alta"),
    "soares2022early": ("Aporta la idea de detección presintomática de roya, el objetivo de largo plazo del proyecto.", "Alta"),
    "chavarro2023influence": ("Justifica comparar arquitecturas, como hizo BioCafe entre MobileNetV2 y EfficientNet-B0.", "Alta"),
    "duhan2025lite": ("Modelo ligero evaluado en café y en Raspberry Pi; referencia directa para la inferencia en el borde.", "Alta"),
    "adelaja2025leveraging": ("Clasificación de enfermedades de hojas de café en tiempo real, el mismo problema de BioCafe.", "Alta"),
    "macdonald2024grow": ("Muestra que un modelo muy pequeño puede ser exacto, útil para teléfonos de gama baja.", "Media"),
    "piccialli2025agrifold": ("Camino para mejorar el modelo con fotos de varias fincas sin centralizarlas.", "Alta"),
    "ghazal2024computer": ("Advierte sobre los retos de llevar modelos de visión a condiciones reales de campo.", "Media"),
}

# Groups of two or three abstracts and how together they benefit the project.
GRUPOS = [
    ("Ajuste y validación del rendimiento de MPI", ["cornebize2022simulation", "hunold2026tuned", "zhong2022using"],
     "Los tres trabajos muestran que el rendimiento de MPI no viene dado al instalarlo: depende de parámetros, del algoritmo "
     "colectivo que elige la biblioteca y del hardware. Para BioCafe significa que el laboratorio de clúster debe incluir "
     "mediciones (por ejemplo, con benchmarks de colectivas) antes de distribuir el entrenamiento, y que se pueden ensayar "
     "configuraciones con emulación antes de ocupar el clúster."),
    ("Allreduce como cuello de botella del entrenamiento", ["nuriyev2024suara", "castello2023analyzing", "utrera2026optimizing"],
     "Los tres estudian Allreduce, la operación que suma los gradientes en cada paso del entrenamiento distribuido. Castelló "
     "et al. lo hacen con CNN, TensorFlow y Horovod, la misma pila de BioCafe; SUARA y Fullpar muestran cómo mejorar el "
     "algoritmo entre nodos y dentro del nodo. Juntos indican que, si BioCafe se reentrena en varios nodos, la elección de la "
     "biblioteca MPI y del algoritmo de Allreduce es la primera palanca de rendimiento."),
    ("Comunicación punto a punto en la red", ["thune2023detailed", "zheng2025towards"],
     "Ambos explican qué ocurre con los mensajes entre pares: la contención por el ancho de banda y la posibilidad de solapar "
     "comunicación y cómputo con operaciones no bloqueantes. En un clúster en red LAN, como el del curso, ayudan a diseñar un "
     "reparto de imágenes con MPI que no deje procesos esperando."),
    ("Estrategias de paralelismo para entrenar redes", ["patil2023study", "maruf2024optimizing", "liang2023survey"],
     "Comparan paralelismo de datos, de modelo y en tubería, con resultados en clasificación de imágenes. Dan a BioCafe el "
     "criterio para elegir: EfficientNet-B0 cabe en una GPU, así que conviene el paralelismo de datos; el de modelo o en "
     "tubería solo se justificaría con modelos mucho más grandes o con hardware muy limitado."),
    ("Programación híbrida con GPU", ["pekkila2022scalable", "garea2023hybrid", "lu2023parallel"],
     "Muestran cómo combinar MPI entre nodos, OpenMP en el nodo y CUDA en la GPU, incluido un caso de clasificación de "
     "imágenes multiespectrales. Para el proyecto, el mensaje es que MPI y la GPU no compiten: MPI coordina varias GPU, y su "
     "versión compatible con CUDA evita copias innecesarias por la CPU."),
    ("Clústeres de bajo costo y MPI desde Python", ["shoop2025hands", "zhang2025topaddpi", "derlatka2024numba"],
     "Los dos primeros enseñan a montar clústeres de Raspberry Pi en red local, lo que cubre las unidades de instalación en "
     "LAN y en clúster del curso; el tercero permite llamar a MPI desde Python, el lenguaje del entrenamiento de BioCafe. "
     "Juntos hacen viable un laboratorio en el que se reparta con MPI la evaluación del modelo sobre miles de imágenes."),
    ("Panorama del paralelismo y de la visión en agricultura", ["romerosandi2024snapshot", "ghazal2024computer"],
     "Son dos revisiones: una, colombiana, sobre los tipos de paralelismo en el entrenamiento profundo; otra sobre la visión "
     "por computador en la agricultura de precisión. Dan al artículo el marco conceptual de las dos áreas del curso y señalan "
     "los retos de llevar los modelos al campo."),
    ("Clasificación de roya y enfermedades del café", ["chavarro2023influence", "adelaja2025leveraging", "araaf2024coffee"],
     "Los tres trabajan con hojas de café: comparan arquitecturas, clasifican en tiempo real y despliegan la detección en un "
     "dispositivo de borde. Validan las decisiones de BioCafe (comparar arquitecturas, ejecutar en el dispositivo) y ofrecen "
     "cifras de referencia para contrastar sus resultados."),
    ("Detección temprana y datos de café", ["soares2022early", "tuestamonteza2023coleaf", "paymode2022transfer"],
     "Soares et al. detectan la roya antes de los síntomas, CoLeaf-DB aporta imágenes de café con otras afectaciones y "
     "Paymode y Malode confirman la eficacia del aprendizaje por transferencia. Juntos señalan hacia dónde puede crecer el "
     "proyecto: más clases, más datos y detección más temprana."),
    ("Modelos ligeros y aprendizaje federado", ["duhan2025lite", "macdonald2024grow", "piccialli2025agrifold"],
     "Los dos primeros muestran modelos pequeños y exactos que corren en dispositivos de bajo costo; el tercero entrena un "
     "modelo entre varios participantes sin compartir imágenes. Para BioCafe confirman que la inferencia debe quedarse en el "
     "teléfono y abren la puerta a mejorar el modelo con fotos de varias fincas sin centralizarlas."),
]

# Five questions to evaluate the review (adapted from the quality checklist in the course guide).
PREGUNTAS = [
    ("¿Se especifica claramente el propósito de la revisión?",
     "Sí. El objetivo y cuatro preguntas descriptivas (PR1 a PR4) están en la introducción, y las conclusiones responden a "
     "cada una.",
     "Se agregó al final de la introducción la frase que relaciona cada pregunta con un grupo de constructos."),
    ("¿Se identificaron las fuentes y se especificó la estrategia de búsqueda?",
     "Sí. Se documentaron la base (Crossref), la fecha (27 de octubre de 2026), los filtros, los prompts y las 38 cadenas "
     "exactas con sus totales, y los scripts permiten repetir la búsqueda.",
     "Se reconoce como limitación usar una sola base; se recomienda repetir las cadenas en Scopus o en el buscador de "
     "ScienceDirect con acceso institucional."),
    ("¿Se definieron los criterios de selección y se aplicaron de forma verificable?",
     "Sí. Los criterios de inclusión y exclusión están en la sección II-D y el flujo (243 → 58 → 28) está respaldado por "
     "archivos de datos con el motivo de cada exclusión por redundancia.",
     "Se reemplazaron 22 artículos sin resumen recuperable por otros del mismo constructo, en lugar de citarlos sin haber "
     "leído su resumen."),
    ("¿Las referencias son actuales, existen y tienen DOI?",
     "Sí. Las 28 tienen DOI verificado en Crossref, fueron publicadas entre 2022 y 2026 y ninguna estaba antes en la "
     "biblioteca de Zotero de las autoras.",
     "Se descartó un resultado con fecha de publicación de 2027 que devolvía la búsqueda; se limpiaron los resúmenes con "
     "palabras pegadas o fórmulas duplicadas."),
    ("¿Las conclusiones se fundamentan en los datos analizados y se reconocen los vacíos?",
     "Sí. Cada cifra del artículo procede del resumen de su referencia o del repositorio de BioCafe, y la sección III-J "
     "declara el vacío (no hay trabajos de MPI en café) y las limitaciones.",
     "Se moderaron afirmaciones que el resumen no respalda; por ejemplo, la reducción de 88 h a 27 h de Lu et al. se debe a "
     "aprovechar la simetría de la matriz, no solo a MPI, y por eso no se presenta como aceleración paralela."),
]

AJUSTES = [
    ("Búsqueda", "Las cadenas genéricas («MPI message passing interface performance», «point-to-point communication MPI "
     "overlap») devolvieron ruido de otros campos (redes de grafos, nubes de puntos). Se descartó por título y se mantuvo "
     "la cadena documentada para que el ruido sea visible y reproducible."),
    ("Búsqueda", "Se agregó al constructo C6 la cadena «coffee leaf rust detection deep learning images», porque las "
     "cadenas generales no traían suficientes trabajos específicos de café."),
    ("Búsqueda", "Se agregaron al constructo C5 dos cadenas sobre clústeres de Raspberry Pi y enseñanza de MPI, porque los "
     "candidatos iniciales de infraestructura no tenían resumen recuperable."),
    ("Selección", "De 25 candidatos iniciales, 10 de ScienceDirect no tenían resumen en ninguna API abierta y la página de "
     "la editorial bloquea la lectura automática. Se reemplazaron por artículos verificados del mismo constructo."),
    ("Selección", "Se excluyeron 8 artículos con resumen por redundancia o alcance; el motivo de cada uno quedó registrado "
     "en datos/cribado.json."),
    ("Verificación", "Se comprobó con el MCP de Zotero (búsqueda por DOI en todas las bibliotecas) que ninguna referencia "
     "estuviera ya en la biblioteca de las autoras."),
    ("Datos", "Se normalizaron los resúmenes: ligaduras tipográficas, fórmulas LaTeX duplicadas y palabras pegadas en dos "
     "resúmenes que venían de Semantic Scholar."),
    ("Redacción", "Se separaron los datos del proyecto (exactitud de 0,94 y 0,81 y 48 ms, del repositorio de BioCafe) de "
     "las cifras de la literatura, para no atribuir a otros autores resultados propios."),
    ("Pendiente", "Agregar los correos institucionales de las autoras en el encabezado del artículo; no se incluyeron "
     "porque no constan en los documentos del proyecto."),
    ("Pendiente", "Insertar las citas con el complemento de Zotero en Word si el docente exige citas dinámicas; las del "
     "documento están numeradas en formato IEEE y coinciden con la colección de Zotero."),
]
