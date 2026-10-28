"""Text of the IEEE article and of the traceability document (version 2: review of the project).

Citations use [@key] or [@key1; @key2] with the keys produced by claves.key();
generar_documentos.py turns them into IEEE numbers in order of first appearance.
Every figure quoted from a study comes from its abstract (datos/referencias.json);
figures about BioCafe come from the project repository (docs/resultados.md).
"""

TITULO = ("Detección temprana de plagas y enfermedades del café con sistemas inteligentes y computación paralela "
          "y distribuida: una revisión sistemática descriptiva")
TITLE_EN = ("Early detection of coffee pests and diseases with intelligent systems and parallel and distributed "
            "computing: a descriptive systematic review")
AUTORES = ["Heyley Yurani Parada Parada", "Lisbeth Gissel Cordero Tovar"]
IDENTIFICACION = {"Heyley Yurani Parada Parada": "1093887319", "Lisbeth Gissel Cordero Tovar": "1093293375"}
CORREO = {"Heyley Yurani Parada Parada": "heyley.paradapar@unipamplona.edu.co",
          "Lisbeth Gissel Cordero Tovar": "lisbeth.corderotov@unipamplona.edu.co"}

def autores_con_id():
    return [f"{n} (C.C. {IDENTIFICACION[n]}, {CORREO[n]})" for n in AUTORES]

AFILIACION = ["Programa de Ingeniería de Sistemas, Facultad de Ingenierías y Arquitectura",
              "Universidad de Pamplona, Villa del Rosario, Norte de Santander, Colombia"]

RESUMEN = (
    "La roya y el minador reducen la productividad del café, y su monitoreo en las fincas sigue siendo mayoritariamente "
    "visual. Este artículo presenta una revisión sistemática descriptiva de la literatura relacionada con el proyecto "
    "«Sistema de detección temprana de plagas y enfermedades en cultivos de café», cuyo prototipo, BioCafe, clasifica fotos "
    "de hojas en el teléfono. A partir de ocho constructos del proyecto, que abarcan el problema agrícola, los sistemas "
    "inteligentes y la computación paralela y distribuida, se formularon prompts y cadenas de búsqueda que se ejecutaron en "
    "Crossref el 27 de octubre de 2026, limitadas a artículos de revista publicados desde 2022 y con prioridad para "
    "ScienceDirect. Se incluyeron 32 artículos con DOI verificado, 16 de ellos de ScienceDirect. La literatura muestra que "
    "las redes neuronales convolucionales clasifican enfermedades de la hoja de café con exactitudes de 90,84 % a 99,95 % en "
    "conjuntos controlados, pero pierden desempeño con imágenes de campo; que las imágenes multiespectrales permiten detectar "
    "la roya antes de los síntomas; que los modelos ligeros funcionan sin conexión en teléfonos y microcontroladores, y que el "
    "entrenamiento en GPU y el entrenamiento distribuido reducen el costo de reentrenar. Se concluye que las decisiones de "
    "BioCafe coinciden con la literatura y que su principal vacío es la validación con fotos de fincas colombianas.")

ABSTRACT = (
    "Coffee leaf rust and leaf miner reduce coffee productivity, and on-farm monitoring is still mostly visual. This paper "
    "presents a descriptive systematic review of the literature related to the project \"Early detection system for pests "
    "and diseases in coffee crops\", whose prototype, BioCafe, classifies leaf photos on the phone. Eight constructs of the "
    "project, covering the agricultural problem, intelligent systems and parallel and distributed computing, were turned "
    "into prompts and search strings that were run on Crossref on October 27, 2026, restricted to journal articles "
    "published since 2022 and giving priority to ScienceDirect. Thirty-two articles with a verified DOI were included, 16 of "
    "them from ScienceDirect. The literature shows that convolutional neural networks classify coffee leaf diseases with "
    "accuracies from 90.84% to 99.95% on controlled datasets but lose performance on field images; that multispectral imaging "
    "detects rust before symptoms appear; that lightweight models run offline on phones and microcontrollers; and that GPU "
    "and distributed training lower the cost of retraining. BioCafe's design choices agree with the literature, and its main "
    "gap is validation with photos from Colombian farms.")

PALABRAS_CLAVE = ("detección temprana, roya del café, minador del café, redes neuronales convolucionales, aprendizaje por "
                  "transferencia, computación en el borde, entrenamiento distribuido, sistemas inteligentes.")
INDEX_TERMS = ("early detection, coffee leaf rust, coffee leaf miner, convolutional neural networks, transfer learning, "
               "edge computing, distributed training, intelligent systems.")

# Each section: (title, [blocks]); a block is a paragraph string, ("sub", "A. ...") a subsection,
# ("tabla", id) a table defined in generar_documentos.py, or ("figura", id) a figure.
SECCIONES = [
    ("Introducción", [
        "La roya del café, causada por el hongo Hemileia vastatrix, es la enfermedad más dañina del cultivo en el mundo: "
        "reduce los rendimientos y puede causar la muerte de la planta [@aristizabal2022monitoring]. En Etiopía, centro de "
        "origen del café arábica, su incidencia media llegó a 35,3 % y se extendió a zonas altas donde antes no se presentaba "
        "[@berihun2022status]. El minador de la hoja (Leucoptera coffeella) es la principal plaga de insectos en varios "
        "países productores y se controla sobre todo con insecticidas sistémicos [@leite2022effects]. Aun así, una revisión "
        "de 51 estudios encontró que el monitoreo de estas afectaciones sigue dependiendo de la observación visual y de "
        "trampas, y que tecnologías como sensores, drones, IoT e inteligencia artificial se usan poco en los cafetales "
        "[@rodriguezgallo2024coffee].",
        "El proyecto «Sistema de detección temprana de plagas y enfermedades en cultivos de café», de la Universidad de "
        "Pamplona, busca cerrar esa brecha. Su prototipo, BioCafe, es una aplicación Android que clasifica una foto de una "
        "hoja en cuatro clases (sana, roya, minador y arañita roja) con una red EfficientNet-B0 que se ejecuta en el teléfono, "
        "sin conexión. La red se entrenó en una GPU de Google Colab con 3736 imágenes de tres conjuntos públicos. Según el "
        "repositorio del proyecto, alcanza una exactitud de 0,94 en la prueba interna y de 0,81 en un conjunto externo, y "
        "tarda 48 ms por imagen en un teléfono Android.",
        "El proyecto combina dos áreas de formación. Desde los Sistemas Inteligentes, usa visión por computador y "
        "aprendizaje profundo para reconocer la afectación. Desde los Fundamentos de Computación Paralela y Distribuida, "
        "depende de la GPU para entrenar y de la ejecución distribuida entre la nube, donde se entrena, y el dispositivo, "
        "donde se diagnostica. Una revisión de la literatura reciente permite contrastar estas decisiones con lo que se ha "
        "publicado y ubicar lo que falta.",
        "El objetivo de esta revisión es describir el estado del conocimiento publicado desde 2022 sobre los componentes del "
        "proyecto y relacionarlo con BioCafe. Se plantean tres preguntas descriptivas: (PR1) ¿qué afectaciones foliares del "
        "café y qué formas de detectarlas temprano describe la literatura reciente?; (PR2) ¿qué datos y modelos de sistemas "
        "inteligentes se usan para clasificarlas y cómo se comportan en condiciones de campo?, y (PR3) ¿qué aporta la "
        "computación paralela y distribuida al entrenamiento y al despliegue de estos sistemas? PR1 se responde con los "
        "constructos C1 y C2; PR2, con C3 a C5, y PR3, con C6 a C8. La sección II describe el método; la sección III presenta "
        "y discute los resultados, y la sección IV resume las conclusiones.",
    ]),
    ("Materiales y métodos", [
        ("sub", "A. Tipo de revisión"),
        "Se realizó una revisión sistemática de tipo descriptivo: su propósito es poner al día al lector sobre lo que se sabe "
        "de un tema en evolución, no responder una pregunta causal ni combinar resultados con metaanálisis. Se siguieron las "
        "cuatro etapas de la guía del curso: definir los objetivos, buscar la bibliografía con una estrategia documentada, "
        "organizar la información y redactar el informe.",
        ("sub", "B. Constructos"),
        "Los constructos se derivaron del título y de los componentes del proyecto: el problema agrícola (las afectaciones y "
        "su detección temprana), el sistema inteligente (datos, modelo y generalización) y la computación paralela y "
        "distribuida (entrenamiento en GPU, inferencia en el dispositivo y arquitecturas distribuidas). Se definieron ocho "
        "constructos, cada uno con una definición operativa e indicadores (Tabla I).",
        ("tabla", "constructos"),
        ("sub", "C. Estrategia de búsqueda"),
        "Para cada constructo se redactó un prompt que expresa el pedido de referencias y, a partir de él, dos cadenas de "
        "búsqueda en inglés. Las cadenas se ejecutaron el 27 de octubre de 2026 en la API de Crossref, que indexa "
        "ScienceDirect, IEEE, Springer, MDPI y otras editoriales. Cada cadena se lanzó dos veces, una limitada al prefijo DOI "
        "de Elsevier (10.1016, ScienceDirect) y otra sin límite de editorial, con dos filtros comunes: artículos de revista y "
        "fecha de publicación desde el 1 de enero de 2022. Se revisaron los diez primeros resultados por relevancia de cada "
        "una de las 32 búsquedas. Los prompts, las cadenas exactas, los totales de resultados y los scripts que repiten el "
        "proceso quedaron documentados en el archivo de constructos y prompts que acompaña este artículo.",
        ("sub", "D. Criterios de selección"),
        "Se incluyeron artículos de revista publicados desde 2022, con DOI que resuelve en Crossref, con resumen recuperable "
        "y relacionados directamente con un constructo; se dio preferencia a ScienceDirect y a los trabajos sobre café. Se "
        "excluyeron el ruido de la búsqueda (por ejemplo, detección temprana de enfermedades humanas), los trabajos sin "
        "resumen recuperable, los redundantes con otro ya incluido y los que estaban fuera del alcance de clasificación de "
        "imágenes. Mediante el servidor MCP de Zotero se verificó que ninguno estuviera ya en la biblioteca de las autoras.",
        ("sub", "E. Verificación y extracción"),
        "Cada DOI se consultó en Crossref para confirmar su existencia, autores, revista y fecha. El resumen se tomó de "
        "Crossref, Semantic Scholar u OpenAlex. De cada artículo se extrajeron el objetivo, el método, el hallazgo principal "
        "con sus cifras y su relación con BioCafe. Las 32 referencias se cargaron en una colección de Zotero y se exportaron "
        "como archivo semilla (RIS y BibTeX) para poder importarlas en cualquier equipo.",
        ("sub", "F. Flujo de selección"),
        "Las 32 búsquedas devolvieron 320 registros revisados, 236 de ellos únicos. A estos se sumaron cuatro artículos "
        "hallados en una primera búsqueda de la revisión, centrada en MPI, que luego se reorientó al proyecto. Por título, "
        "revista y año se preseleccionaron 45, a los que se les verificó el DOI. Se excluyeron 10 por no tener resumen "
        "recuperable y 3 por redundancia o alcance, y quedaron 32 artículos incluidos (Fig. 1).",
        ("figura", "flujo"),
    ]),
    ("Resultados y discusión", [
        ("sub", "A. Panorama de los estudios incluidos"),
        "De los 32 artículos, 16 tienen DOI de ScienceDirect (Elsevier), 6 son de MDPI, 4 de IEEE y los 6 restantes de "
        "otras editoriales, entre ellas la Revista Colombiana de Computación. Todos fueron publicados entre 2022 y 2026. "
        "Catorce tratan directamente sobre café; los otros dieciocho abordan la detección de enfermedades en otros cultivos o "
        "la computación paralela y distribuida que la soporta. La Tabla II reúne los hallazgos cuantitativos más relevantes "
        "para BioCafe.",
        ("tabla", "hallazgos"),
        ("sub", "B. Afectaciones foliares del café y su manejo (C1)"),
        "La roya es la afectación más estudiada. En Hawái, donde llegó en 2020, el monitoreo de 30 lotes mostró una "
        "incidencia inferior a 4 % al inicio de la temporada que subió a 36 % en la cosecha, por encima del umbral de acción "
        "de 5 % aun con 3 a 10 aplicaciones preventivas de fungicida [@aristizabal2022monitoring]. En ensayos posteriores en "
        "las mismas fincas, un fungicida translaminar mantuvo la roya por debajo de 2 % durante 12 semanas, y los fungicidas "
        "de cobre fueron los más rentables [@aristizabal2025fungicide]. En Etiopía la incidencia media alcanzó 35,3 % y el "
        "cambio climático favorece su expansión a nuevas altitudes [@berihun2022status]. Sobre el minador, Leite et al. "
        "advierten que el uso innecesario de insecticidas sistémicos puede seleccionar resistencia en la plaga "
        "[@leite2022effects]. La revisión de Rodriguez-Gallo et al. concluye que el manejo de estas afectaciones sigue "
        "apoyado en técnicas tradicionales y que la integración de sensores, drones, IoT e inteligencia artificial es todavía "
        "escasa [@rodriguezgallo2024coffee]. El conjunto justifica un sistema que detecte a tiempo para aplicar solo cuando "
        "es necesario.",
        ("sub", "C. Detección temprana (C2)"),
        "Dos estudios muestran que la detección puede adelantarse a los síntomas. Soares et al. distinguieron plántulas "
        "infectadas de roya a los 15 días de la inoculación, antes de las lesiones visibles, con imágenes multiespectrales "
        "tomadas desde un dron y una máquina de vectores de soporte, con 80 % de exactitud [@soares2022early]. Santos et al. "
        "diferenciaron hojas sanas de hojas atacadas por el minador con índices de vegetación multiespectrales; el NDVI medio "
        "fue de 0,64 en hojas sanas y de 0,41 en hojas infestadas, y el índice GRNDVI fue el que mejor las separó "
        "[@santos2022vegetation]. Las revisiones generales coinciden en que el aprendizaje profundo supera a las técnicas "
        "clásicas de aprendizaje automático en la detección de enfermedades a partir de imágenes [@jackulin2022comprehensive] "
        "y en que la falta de datos de campo etiquetados es el principal obstáculo para llevar estos modelos, incluidos los "
        "basados en biosensores, a la agricultura de precisión [@sharma2026machine]. BioCafe trabaja con fotos RGB del "
        "teléfono, de modo que detecta cuando hay síntomas visibles; la detección presintomática exigiría otro sensor.",
        ("sub", "D. Conjuntos de datos de hojas de café (C3)"),
        "Los datos son el insumo crítico. Aroca-Trujillo y Perez-Ruiz publicaron 6726 imágenes multiespectrales de hojas de "
        "café de fincas colombianas, con y sin lesiones de roya, capturadas en RGB y en cinco bandas bajo iluminación "
        "controlada [@arocatrujillo2025colombian]. CoLeaf-DB aporta 1006 imágenes de hojas de café del Perú etiquetadas por "
        "agrónomos según deficiencias nutricionales [@tuestamonteza2023coleaf]. El primero es directamente aprovechable por "
        "BioCafe para ampliar la clase roya con muestras colombianas; el segundo, para añadir clases distintas de plagas y "
        "enfermedades.",
        ("sub", "E. Clasificación con redes convolucionales (C4)"),
        "Los trabajos sobre café reportan exactitudes altas en conjuntos controlados. Coffee-Net clasifica hojas sanas y con "
        "Phoma, minador, roya y Cercospora con 99,95 % de exactitud [@bidarakundi2025coffee]. CoffNet alcanza 97,88 % a "
        "125,93 imágenes por segundo [@adelaja2025leveraging]. Bordin Yamashita y Leite clasificaron seis enfermedades "
        "con más de 6000 imágenes y redes ejecutadas en una placa de bajo costo, sin conexión, con exactitudes cercanas a "
        "98 % y 96 % [@bordinyamashita2023coffee]. Araaf et al. detectaron roya con YOLOv8 con un mAP de 73,2 % "
        "[@araaf2024coffee]. Chavarro et al. compararon más de 800 modelos de transferencia para la roya y hallaron que la "
        "arquitectura base es el hiperparámetro de mayor efecto, con diferencias de hasta 70 % [@chavarro2023influence], y "
        "Paymode y Malode confirman la eficacia del aprendizaje por transferencia en otros cultivos [@paymode2022transfer]. "
        "BioCafe sigue este enfoque: eligió EfficientNet-B0 tras compararla con MobileNetV2.",
        ("sub", "F. Generalización a condiciones de campo (C5)"),
        "Las exactitudes anteriores no se trasladan al campo. Ahmad et al. mostraron que los modelos entrenados con imágenes "
        "de laboratorio no generalizan con la misma exactitud a otros conjuntos: la mejor generalización fue de 81,60 %, y "
        "eliminar el fondo o mezclar imágenes de laboratorio y de campo la mejora [@ahmad2023toward]. Con adaptación de "
        "dominio no supervisada, Wu et al. obtuvieron exactitudes de 56,06 % en PlantDoc y de 96,78 % en otro conjunto, lo "
        "que muestra cuánto varía el desempeño entre fuentes [@wu2023from]. Jeon et al. recomponen el fondo de las imágenes "
        "para acercarlas a las del cultivo y logran un desempeño robusto en campo sin datos de campo etiquetados "
        "[@jeon2026bridging], y Bouacida et al. reconocen hojas enfermas de cultivos no vistos enfocándose en las regiones "
        "lesionadas, con 97,13 % de exactitud en conjuntos nuevos [@bouacida2025innovative]. BioCafe muestra el mismo "
        "fenómeno: pasa de 0,94 en la prueba interna a 0,81 en un conjunto externo.",
        ("sub", "G. Entrenamiento con GPU y computación paralela (C6)"),
        "Entrenar estos modelos es la parte costosa del sistema. Las revisiones sobre paralelismo distinguen el paralelismo "
        "de datos, en el que cada GPU entrena una copia del modelo con una parte de las imágenes, del paralelismo de modelo, "
        "que reparte el modelo entre dispositivos [@romerosandi2024snapshot; @liang2023survey]. En un caso de clasificación "
        "de imágenes médicas, el paralelismo de modelo logró una aceleración de 1,38 veces y una exactitud de validación de "
        "62,13 % frente a 55,72 % [@patil2023study]. Cuando el entrenamiento se distribuye en un clúster con TensorFlow y "
        "Horovod, la operación colectiva Allreduce de MPI, que suma los gradientes, determina el rendimiento: elegir bien su "
        "implementación acelera el entrenamiento de redes convolucionales entre 1,2 y 2,8 veces "
        "[@castello2023analyzing]. Para BioCafe, que entrena EfficientNet-B0 en una sola GPU, el paralelismo de datos es la "
        "vía para reentrenar con más imágenes sin alargar el tiempo de entrenamiento.",
        ("sub", "H. Despliegue móvil, en el borde y distribuido (C7 y C8)"),
        "Los modelos ligeros permiten diagnosticar sin conexión. RTR_Lite_MobileNet logra 90,84 % de exactitud en un "
        "conjunto de café y funciona en Raspberry Pi 4 y 5 con baja latencia y bajo consumo de memoria [@duhan2025lite]. "
        "Khan et al. redujeron con cuantización los parámetros de MobileNetV3-small de cerca de 1,5 millones a 0,93 "
        "millones sin perder su exactitud de 99,50 % [@khan2023plant]. Nayak et al. compararon modelos para arroz y "
        "encontraron que MobileNetV2 es el más adecuado para una aplicación de teléfono que funciona sin conexión, mientras "
        "que ResNet50 rindió mejor en la nube; su sistema reentrena el modelo en un servidor con imágenes nuevas y lo "
        "actualiza en el teléfono [@nayak2023application]. Otras aplicaciones envían la foto a un servidor: Cocoa Companion "
        "diagnostica en la nube [@kumi2022cocoa] y la de Ramana Reddy et al. usa un servicio web para la inferencia "
        "[@ramanareddy2025deep]. En el extremo distribuido, AGRIFOLD entrena una red ligera entre varios participantes con "
        "aprendizaje federado, sin compartir las imágenes [@piccialli2025agrifold], y Ghazal et al. señalan los retos de "
        "desplegar modelos generales de visión en tiempo real en fincas [@ghazal2024computer]. BioCafe adopta el esquema "
        "de Nayak et al.: entrena en la nube y diagnostica en el teléfono.",
        ("sub", "I. Implicaciones para BioCafe"),
        "La literatura respalda las decisiones principales del prototipo: aprendizaje por transferencia con una arquitectura "
        "elegida por comparación [@chavarro2023influence], diagnóstico en el dispositivo sin conexión "
        "[@bordinyamashita2023coffee; @nayak2023application] y entrenamiento en GPU. También señala tres mejoras concretas. "
        "Primero, incorporar fotos colombianas, empezando por el conjunto de Aroca-Trujillo y Perez-Ruiz "
        "[@arocatrujillo2025colombian], y validar con fotos de fincas de Norte de Santander. Segundo, aplicar técnicas de "
        "generalización como la recomposición del fondo o la adaptación de dominio [@ahmad2023toward; @jeon2026bridging]. "
        "Tercero, cuando el volumen de datos crezca, distribuir el reentrenamiento con paralelismo de datos "
        "[@castello2023analyzing] y, a más largo plazo, explorar el aprendizaje federado entre fincas "
        "[@piccialli2025agrifold].",
        ("sub", "J. Vacíos y limitaciones"),
        "No se encontraron trabajos sobre la arañita roja en café con visión por computador, la clase más débil de BioCafe, "
        "ni validaciones en fincas colombianas de modelos entrenados con datos públicos. Los estudios sobre café reportan "
        "exactitudes en conjuntos controlados y rara vez en un conjunto externo. Esta revisión tiene límites propios: usó "
        "una sola base (Crossref), revisó los diez primeros resultados de cada búsqueda y excluyó 10 artículos cuyo resumen "
        "no estaba disponible en APIs abiertas.",
    ]),
    ("Conclusiones", [
        "La revisión identificó 32 artículos recientes, con DOI verificado, que describen el estado del conocimiento sobre "
        "los componentes del proyecto. Respecto a PR1, la roya y el minador siguen causando pérdidas y su monitoreo es "
        "mayoritariamente visual; las imágenes multiespectrales permiten detectar la roya antes de los síntomas. Respecto a "
        "PR2, las redes convolucionales con aprendizaje por transferencia clasifican las enfermedades de la hoja de café con "
        "exactitudes de 90,84 % a 99,95 % en conjuntos controlados, pero su desempeño cae con imágenes de otras fuentes, un "
        "problema que la adaptación de dominio y la mezcla de datos de campo empiezan a resolver. Respecto a PR3, el "
        "entrenamiento en GPU y el entrenamiento distribuido reducen el costo de reentrenar, los modelos ligeros y "
        "cuantizados permiten diagnosticar sin conexión, y el aprendizaje federado abre la posibilidad de mejorar el modelo "
        "con datos de varias fincas.",
        "Las decisiones de BioCafe coinciden con lo que reporta la literatura. Su principal vacío, compartido con la "
        "mayoría de los trabajos revisados, es la validación en campo: se propone como trabajo futuro reentrenar con fotos "
        "colombianas, medir el desempeño en fincas de Norte de Santander y reforzar la clase arañita roja, para la que no "
        "se encontraron estudios específicos.",
    ]),
]

HALLAZGOS = [
    ("aristizabal2022monitoring", "Roya en Hawái: la incidencia pasó de menos de 4 % a 36 % en la cosecha pese a 3 a 10 aplicaciones preventivas"),
    ("berihun2022status", "Roya en Etiopía: incidencia media de 35,3 % y expansión a zonas altas"),
    ("soares2022early", "Roya detectada 15 días tras la inoculación, antes de los síntomas: 80 % de exactitud"),
    ("bidarakundi2025coffee", "Coffee-Net, cinco clases (incluye minador y roya): 99,95 % de exactitud"),
    ("bordinyamashita2023coffee", "CNN en una placa de bajo costo, sin internet: exactitud cercana a 98 %"),
    ("adelaja2025leveraging", "CoffNet: 97,88 % de exactitud a 125,93 imágenes por segundo"),
    ("ahmad2023toward", "Generalización entre conjuntos de datos: máximo de 81,60 %"),
    ("wu2023from", "Adaptación de dominio: 56,06 % en PlantDoc frente a 96,78 % en otro conjunto"),
    ("castello2023analyzing", "Elegir la implementación de Allreduce acelera el entrenamiento de 1,2 a 2,8 veces"),
    ("khan2023plant", "Cuantización: de 1,5 a 0,93 millones de parámetros sin perder 99,50 % de exactitud"),
    ("nayak2023application", "MobileNetV2, el modelo más adecuado para el teléfono sin conexión"),
]

RESUMEN_ES = {
    "rodriguezgallo2024coffee": "Revisión sistemática (PRISMA) de 51 estudios sobre el manejo de la roya y la broca en sistemas agroforestales; el monitoreo sigue siendo visual y con trampas, y el uso de sensores, drones, IoT e IA es escaso.",
    "aristizabal2022monitoring": "Monitoreo de la roya en 30 lotes de Hawái tras su llegada en 2020: la incidencia subió de menos de 4 % a 36 % en la cosecha, por encima del umbral de 5 %, pese a 3 a 10 aplicaciones preventivas de fungicida.",
    "aristizabal2025fungicide": "Ensayos de fungicidas contra la roya en fincas de Hawái: el translaminar mantuvo la roya por debajo de 2 % durante 12 semanas y los de cobre fueron los más rentables.",
    "berihun2022status": "Revisión del estado de la roya en Etiopía: incidencia media de 35,3 %, expansión a zonas medias y altas, influencia del cambio climático y estrategias de manejo.",
    "leite2022effects": "Evalúa el insecticida tiametoxam contra el minador de la hoja en plántulas de café en Brasil; advierte que su uso innecesario puede seleccionar resistencia en la plaga.",
    "soares2022early": "Detecta roya en plántulas a los 15 días de la inoculación, antes de los síntomas, con imágenes multiespectrales desde un dron y SVM, con 80 % de exactitud.",
    "santos2022vegetation": "Diferencia hojas de café sanas y atacadas por el minador con índices de vegetación multiespectrales; el GRNDVI fue el índice que mejor las separó.",
    "jackulin2022comprehensive": "Revisión de técnicas de aprendizaje automático y profundo para detectar enfermedades de plantas; concluye que el aprendizaje profundo supera a los métodos clásicos.",
    "sharma2026machine": "Revisión sistemática de biosensores con aprendizaje automático e IoT para detectar estrés y patógenos; señala la falta de datos de campo etiquetados como principal reto.",
    "arocatrujillo2025colombian": "Conjunto de 6726 imágenes multiespectrales (RGB y cinco bandas) de hojas de café de fincas colombianas, con y sin lesiones de roya.",
    "tuestamonteza2023coleaf": "CoLeaf-DB: 1006 imágenes de hojas de café del Perú etiquetadas por agrónomos según deficiencias nutricionales.",
    "bordinyamashita2023coffee": "Embebe redes convolucionales en una placa de bajo costo para clasificar seis enfermedades del café sin internet, con exactitudes cercanas a 98 % y 96 %.",
    "adelaja2025leveraging": "Propone CoffNet para identificar enfermedades de hojas de café en tiempo real, con 97,88 % de exactitud y 125,93 imágenes por segundo.",
    "chavarro2023influence": "Compara más de 800 modelos de transferencia para clasificar roya del café; la arquitectura base causa diferencias de hasta 70 % y el optimizador de hasta 20 %.",
    "bidarakundi2025coffee": "Coffee-Net clasifica hojas de café sanas y con Phoma, minador, roya y Cercospora con 99,95 % de exactitud.",
    "paymode2022transfer": "Aprendizaje por transferencia con VGG para clasificar enfermedades en hojas de uva y tomate, con 98,40 % y 95,71 % de exactitud.",
    "araaf2024coffee": "Detecta roya del café con YOLOv8 (mAP de 73,2 %) y despliega el modelo en un dispositivo de borde integrado a una podadora.",
    "ahmad2023toward": "Evalúa la generalización de modelos de enfermedades del maíz entre cinco conjuntos de datos; la mejor fue de 81,60 % y mejora al quitar el fondo o mezclar datos de campo.",
    "wu2023from": "Propone MSUN, adaptación de dominio no supervisada del laboratorio al campo; logra 56,06 % en PlantDoc y 96,78 % en otro conjunto.",
    "jeon2026bridging": "Recompone el fondo de las imágenes y aplica adaptación de dominio para diagnosticar enfermedades en campo sin datos de campo etiquetados.",
    "bouacida2025innovative": "Reconoce hojas enfermas de cultivos no vistos centrándose en las regiones lesionadas, con 94,04 % en PlantVillage y 97,13 % en conjuntos nuevos.",
    "patil2023study": "Compara paralelismo de datos y de modelo para clasificar imágenes de retinopatía; el de modelo logra 62,13 % de exactitud frente a 55,72 % y 1,38 veces de aceleración.",
    "romerosandi2024snapshot": "Panorama colombiano del paralelismo en el entrenamiento distribuido (datos, modelo, tubería, híbrido) con experimentos de paralelismo de datos y de modelo.",
    "castello2023analyzing": "Analiza Allreduce en tres bibliotecas MPI para entrenar CNN con TensorFlow y Horovod; elegir bien acelera el entrenamiento de 1,2 a 2,8 veces.",
    "liang2023survey": "Revisión del autoparalelismo en el entrenamiento de modelos grandes: esquemas de paralelismo, costo de comunicación y memoria, y búsqueda de estrategias.",
    "duhan2025lite": "RTR_Lite_MobileNet, una MobileNetV2 con atención, logra 90,84 % en café y funciona en Raspberry Pi 4 y 5 con baja latencia y memoria.",
    "nayak2023application": "Aplicación de teléfono para enfermedades del arroz: MobileNetV2 fue el mejor modelo para el teléfono sin conexión; un servidor reentrena y actualiza el modelo.",
    "khan2023plant": "MobileNetV3-small cuantizado pasa de 1,5 a 0,93 millones de parámetros manteniendo 99,50 % de exactitud, para dispositivos de borde.",
    "ramanareddy2025deep": "Aplicación móvil multiplataforma con una CNN propia (92,06 %) y estimación de severidad, con la inferencia en un servicio web.",
    "piccialli2025agrifold": "AGRIFOLD: aprendizaje federado de una CNN ligera para hojas enfermas sin compartir las imágenes; compara cinco métodos de agregación en 12 conjuntos.",
    "ghazal2024computer": "Revisión de la visión por computador en la agricultura de precisión y de los retos para desplegar modelos en tiempo real en fincas.",
    "kumi2022cocoa": "Aplicación de teléfono para enfermedades del cacao que envía la foto a un servicio en la nube, donde un modelo SSD MobileNet V2 hace el diagnóstico.",
}

RELACION = {
    "rodriguezgallo2024coffee": ("Justifica el proyecto: el monitoreo de la roya sigue siendo visual y la IA apenas se usa en los cafetales.", "Alta"),
    "aristizabal2022monitoring": ("Muestra el costo de detectar tarde: la roya supera el umbral aun con fungicida preventivo.", "Alta"),
    "aristizabal2025fungicide": ("Un diagnóstico oportuno permite elegir el fungicida y el momento de aplicarlo.", "Media"),
    "berihun2022status": ("Dimensiona la amenaza de la roya y su avance a zonas altas, como las de Norte de Santander.", "Media"),
    "leite2022effects": ("Respalda detectar el minador para no aplicar insecticidas de forma innecesaria.", "Media"),
    "soares2022early": ("Referencia de detección presintomática de roya, el objetivo de largo plazo del proyecto.", "Alta"),
    "santos2022vegetation": ("Muestra que el minador también es detectable con imágenes, una de las clases de BioCafe.", "Alta"),
    "jackulin2022comprehensive": ("Respalda el uso de aprendizaje profundo frente a técnicas clásicas.", "Media"),
    "sharma2026machine": ("Identifica la falta de datos de campo etiquetados, el mismo límite de BioCafe.", "Media"),
    "arocatrujillo2025colombian": ("Datos colombianos de roya que BioCafe puede usar para reentrenar y validar.", "Alta"),
    "tuestamonteza2023coleaf": ("Datos de café que permitirían añadir clases de deficiencias nutricionales.", "Media"),
    "bordinyamashita2023coffee": ("Diagnóstico de enfermedades del café sin internet en hardware de bajo costo, como BioCafe.", "Alta"),
    "adelaja2025leveraging": ("Clasificación de enfermedades de hojas de café en tiempo real: el mismo problema de BioCafe.", "Alta"),
    "chavarro2023influence": ("Justifica comparar arquitecturas, como hizo BioCafe entre MobileNetV2 y EfficientNet-B0.", "Alta"),
    "bidarakundi2025coffee": ("Clasifica minador y roya, dos clases de BioCafe; cifra de referencia en datos controlados.", "Alta"),
    "paymode2022transfer": ("Respalda el aprendizaje por transferencia que usa BioCafe.", "Media"),
    "araaf2024coffee": ("Detección de roya en un dispositivo de borde, comparable con la app móvil de BioCafe.", "Alta"),
    "ahmad2023toward": ("Explica la caída de BioCafe en el conjunto externo y propone cómo mitigarla.", "Alta"),
    "wu2023from": ("Técnica de adaptación de dominio para mejorar el desempeño con fotos de campo.", "Media"),
    "jeon2026bridging": ("Permite adaptar el modelo al campo sin etiquetar fotos de fincas.", "Alta"),
    "bouacida2025innovative": ("Centrarse en las lesiones mejora la generalización, útil para fotos con fondos variados.", "Media"),
    "patil2023study": ("Compara estrategias de paralelismo para clasificar imágenes, aplicable al reentrenamiento.", "Media"),
    "romerosandi2024snapshot": ("Fuente colombiana y didáctica sobre los tipos de paralelismo en el entrenamiento.", "Alta"),
    "castello2023analyzing": ("Es la referencia para distribuir el entrenamiento con TensorFlow, la herramienta de BioCafe.", "Alta"),
    "liang2023survey": ("Marco conceptual para elegir entre paralelismo de datos y de modelo.", "Media"),
    "duhan2025lite": ("Modelo ligero evaluado en café y en dispositivos de borde.", "Alta"),
    "nayak2023application": ("Mismo esquema que BioCafe: entrenar en la nube y diagnosticar en el teléfono sin conexión.", "Alta"),
    "khan2023plant": ("La cuantización reduciría el tamaño del modelo de BioCafe para teléfonos de gama baja.", "Media"),
    "ramanareddy2025deep": ("Alternativa con inferencia en servidor, útil para contrastar con el diseño sin conexión.", "Media"),
    "piccialli2025agrifold": ("Camino para mejorar el modelo con fotos de varias fincas sin centralizarlas.", "Alta"),
    "ghazal2024computer": ("Advierte los retos de llevar modelos de visión a las condiciones reales de campo.", "Media"),
    "kumi2022cocoa": ("Ejemplo de diagnóstico en la nube, que exige conexión en la finca.", "Media"),
}

GRUPOS = [
    ("La roya como problema y el costo de detectarla tarde", ["aristizabal2022monitoring", "aristizabal2025fungicide", "berihun2022status"],
     "Los tres describen la roya en dos regiones distintas: su avance a pesar del fungicida preventivo, la eficacia y el costo "
     "de cada producto, y su expansión a zonas altas por el cambio climático. Juntos justifican el objetivo de BioCafe: "
     "detectar a tiempo para aplicar el producto adecuado solo cuando hace falta."),
    ("Monitoreo actual y manejo del minador", ["rodriguezgallo2024coffee", "leite2022effects"],
     "La revisión de Rodriguez-Gallo et al. muestra que el monitoreo sigue siendo visual y que la inteligencia artificial "
     "apenas se usa en los cafetales; Leite et al. advierten del uso innecesario de insecticidas contra el minador. Ambos "
     "sitúan a BioCafe como herramienta para decidir con información en lugar de aplicar por calendario."),
    ("Detección antes de los síntomas", ["soares2022early", "santos2022vegetation"],
     "Ambos usan imágenes multiespectrales: uno detecta la roya antes de los síntomas y el otro separa hojas sanas de hojas "
     "con minador. Muestran hacia dónde puede crecer el proyecto si incorpora sensores más allá de la cámara del teléfono."),
    ("Panorama de la detección con aprendizaje automático", ["jackulin2022comprehensive", "sharma2026machine", "ghazal2024computer"],
     "Son tres revisiones: el aprendizaje profundo supera a las técnicas clásicas, la falta de datos de campo etiquetados es el "
     "principal obstáculo y desplegar modelos generales en fincas reales sigue siendo un reto. Dan el marco conceptual de "
     "Sistemas Inteligentes del artículo."),
    ("Datos de café para entrenar", ["arocatrujillo2025colombian", "tuestamonteza2023coleaf"],
     "Ofrecen imágenes de hojas de café: el primero, de fincas colombianas con roya; el segundo, de deficiencias "
     "nutricionales en el Perú. Son la fuente más directa para reentrenar BioCafe con datos más cercanos a su contexto y "
     "para ampliar sus clases."),
    ("Clasificación de enfermedades de la hoja de café", ["bidarakundi2025coffee", "adelaja2025leveraging", "chavarro2023influence"],
     "Los tres clasifican enfermedades de la hoja de café con aprendizaje profundo y reportan cifras altas en datos "
     "controlados; Chavarro et al. muestran además que la arquitectura base es la decisión que más pesa. Validan el enfoque "
     "de BioCafe y le dan cifras de referencia."),
    ("Diagnóstico sin conexión en el dispositivo", ["bordinyamashita2023coffee", "araaf2024coffee", "duhan2025lite"],
     "Los tres ejecutan el modelo en hardware de bajo costo o de borde (una placa, un dispositivo de poda, una Raspberry Pi), "
     "dos de ellos con café. Confirman que diagnosticar en el lugar y sin internet es viable, como hace BioCafe en el "
     "teléfono."),
    ("Del laboratorio al campo", ["ahmad2023toward", "wu2023from", "jeon2026bridging"],
     "Los tres miden o atacan la caída de desempeño cuando el modelo se usa con fotos de otras fuentes: eliminación del "
     "fondo, mezcla de datos y adaptación de dominio. Explican la diferencia entre 0,94 y 0,81 que muestra BioCafe y ofrecen "
     "técnicas para reducirla."),
    ("Generalizar y transferir", ["bouacida2025innovative", "paymode2022transfer"],
     "Uno generaliza a cultivos no vistos centrándose en las lesiones; el otro confirma la eficacia del aprendizaje por "
     "transferencia. Juntos respaldan reutilizar redes preentrenadas y enfocar el modelo en la zona afectada de la hoja."),
    ("Paralelismo para entrenar", ["romerosandi2024snapshot", "patil2023study", "liang2023survey"],
     "Explican y comparan el paralelismo de datos y de modelo. Para BioCafe, cuyo modelo cabe en una GPU, indican que el "
     "paralelismo de datos es la opción para reentrenar con más imágenes."),
    ("Entrenamiento distribuido y federado", ["castello2023analyzing", "piccialli2025agrifold"],
     "El primero muestra cómo distribuir el entrenamiento con TensorFlow en un clúster; el segundo, cómo entrenar entre "
     "varios participantes sin compartir los datos. Son las dos vías para crecer cuando BioCafe reciba fotos de muchas "
     "fincas."),
    ("Modelos para ejecutar en el teléfono", ["nayak2023application", "khan2023plant"],
     "Nayak et al. entrenan en el servidor y diagnostican en el teléfono sin conexión, el mismo esquema de BioCafe, y Khan "
     "et al. reducen el tamaño del modelo con cuantización sin perder exactitud. Juntos indican cómo llevar el modelo a "
     "teléfonos de gama baja."),
    ("Aplicaciones que diagnostican en la nube", ["kumi2022cocoa", "ramanareddy2025deep"],
     "Ambas aplicaciones envían la foto a un servidor para el diagnóstico; la segunda estima además la severidad. Muestran "
     "la alternativa que BioCafe descartó porque exige conexión en la finca, y sugieren la severidad como mejora futura."),
]

PREGUNTAS = [
    ("¿Se especifica claramente el propósito de la revisión?",
     "Sí. El objetivo y tres preguntas descriptivas (PR1 a PR3) están en la introducción, cada una ligada a sus constructos, "
     "y las conclusiones responden a cada una.",
     "La primera versión giraba en torno a MPI; se reorientó al proyecto completo porque la revisión debía tratar sobre el "
     "proyecto, no sobre una tecnología."),
    ("¿Se identificaron las fuentes y se especificó la estrategia de búsqueda?",
     "Sí. Se documentaron la base (Crossref), la fecha (27 de octubre de 2026), los filtros, los prompts y las 32 cadenas "
     "exactas con sus totales, y los scripts permiten repetir la búsqueda.",
     "Se reconoce como limitación usar una sola base; se recomienda repetir las cadenas en Scopus o en el buscador de "
     "ScienceDirect con acceso institucional."),
    ("¿Se definieron los criterios de selección y se aplicaron de forma verificable?",
     "Sí. Los criterios están en la sección II-D y el flujo (236 únicos + 4 de la primera búsqueda → 45 → 32) está "
     "respaldado por archivos de datos con el motivo de cada exclusión.",
     "Se excluyeron 10 artículos sin resumen recuperable en lugar de citarlos sin haber leído su resumen, y se reasignaron "
     "dos artículos al constructo que mejor los describe."),
    ("¿Las referencias son actuales, existen y tienen DOI?",
     "Sí. Las 32 tienen DOI verificado en Crossref y en doi.org, fueron publicadas entre 2022 y 2026 y ninguna estaba antes "
     "en la biblioteca de Zotero de las autoras.",
     "Se retiraron de Zotero (a la papelera, recuperables) las referencias de la primera versión que ya no se usan, para que "
     "la colección contenga solo las citadas."),
    ("¿Las conclusiones se fundamentan en los datos analizados y se reconocen los vacíos?",
     "Sí. Cada cifra procede del resumen de su referencia o del repositorio de BioCafe, y la sección III-J declara los "
     "vacíos (arañita roja, validación en fincas colombianas) y las limitaciones.",
     "Se separaron los resultados propios de BioCafe de las cifras de la literatura y se moderaron afirmaciones que el "
     "resumen no respalda."),
]

AJUSTES = [
    ("Enfoque", "La primera versión de la revisión se centró en MPI. Por indicación de las autoras, se reorientó al proyecto "
     "en su conjunto: los constructos ahora cubren el problema agrícola, el sistema inteligente y la computación paralela y "
     "distribuida como partes del proyecto. La versión anterior se conserva en datos/v1_mpi/ como evidencia."),
    ("Búsqueda", "Se redactaron ocho constructos nuevos con sus prompts y 16 cadenas (32 búsquedas con y sin filtro de "
     "ScienceDirect), revisando diez resultados por búsqueda en lugar de ocho."),
    ("Búsqueda", "Algunas cadenas generales («early plant disease detection machine learning sensors», «IoT edge cloud "
     "computing crop disease monitoring») trajeron ruido de otros campos (medicina, industria); se descartó por título y la "
     "cadena quedó documentada."),
    ("Selección", "Se reutilizaron 13 referencias de la primera versión que siguen siendo pertinentes para el proyecto; cuatro "
     "de ellas no aparecieron en las búsquedas nuevas y se declaran como provenientes de la primera búsqueda."),
    ("Selección", "Se excluyeron 10 preseleccionados sin resumen recuperable y 3 por redundancia o alcance; el motivo de cada "
     "uno quedó en datos/cribado.json."),
    ("Verificación", "Se comprobó con el MCP de Zotero que ninguna de las 19 referencias nuevas estuviera en la biblioteca de "
     "las autoras. La colección se renombró a «BioCafe - Revisión sistemática del proyecto»."),
    ("Zotero", "Los 28 elementos de la primera versión se enviaron a la papelera de Zotero (recuperables) y se importaron las "
     "32 referencias finales con etiquetas por constructo, para que la colección contenga solo las citadas."),
    ("Redacción", "Se separaron los datos del proyecto (exactitud de 0,94 y 0,81, 48 ms, 3736 imágenes, del repositorio de "
     "BioCafe) de las cifras de la literatura."),
    ("Redacción", "Se agregaron al encabezado de los tres documentos la cédula de ciudadanía y el correo institucional de "
     "cada autora, suministrados por ellas."),
    ("Pendiente", "Insertar las citas con el complemento de Zotero en Word si el docente exige citas dinámicas; las del "
     "documento están numeradas en formato IEEE y coinciden con la colección de Zotero."),
]
