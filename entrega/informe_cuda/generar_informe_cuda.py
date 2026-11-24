#!/usr/bin/env python3
"""Build the IEEE-format report on CUDA (Informe_IEEE_CUDA.docx).

Figures are drawn with matplotlib and Graphviz into figuras/. The benchmark
numbers come from experimento/resultados.json, produced by experimento/matmul.cu
on the authors' machine, so the text never hardcodes a measurement.

Run: python3 generar_informe_cuda.py
"""
import json
import math
import re
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
FIG = HERE / "figuras"
OUT = HERE / "Informe_IEEE_CUDA.docx"
RES = json.loads((HERE / "experimento" / "resultados.json").read_text())
FONT = "Times New Roman"
MONO = "Courier New"
DOT = "/usr/bin/dot"
GVF = "Times New Roman,serif"  # Graphviz needs the fallback to resolve Times
ROMAN = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI".split()

plt.rcParams.update({"font.family": "serif", "font.serif": [FONT, "Liberation Serif"],
                     "font.size": 8, "savefig.dpi": 220})
GREEN, BLUE, GREY, ORANGE = "#76B900", "#2F5597", "#7F7F7F", "#C55A11"

# ------------------------------------------------------------------ measurements
MM = {r["n"]: r for r in RES["matmul"]}
VA = RES["vec_add"]


def gflops(n, ms):
    return 2.0 * n ** 3 / (ms * 1e-3) / 1e9


def es(x, d=1):
    """Spanish decimal comma."""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


B = MM[2048]
SP_NAIVE = B["cpu_ms"] / B["naive_ms"]
SP_TILED = B["cpu_ms"] / B["tiled_ms"]
SP_CUBLAS = B["cpu_ms"] / B["cublas_ms"]
CUBLAS_TOTAL = B["cublas_ms"] + B["h2d_ms"] + B["d2h_ms"]
SP_CUBLAS_TOTAL = B["cpu_ms"] / CUBLAS_TOTAL
VA_GPU_TOTAL = VA["h2d_ms"] + VA["kernel_ms"] + VA["d2h_ms"]
VA_COPY_SHARE = (VA["h2d_ms"] + VA["d2h_ms"]) / VA_GPU_TOTAL * 100
CUDA_VER = f"{RES['cuda_runtime'] // 1000}.{RES['cuda_runtime'] % 1000 // 10}"
CORES = RES["sms"] * 128  # Ada Lovelace: 128 FP32 CUDA cores per SM
ERR_EXP = math.floor(math.log10(max(max(r["naive_err"], r["tiled_err"], r["cublas_err"]) for r in RES["matmul"])))
SUP = {e: "⁻" + str(-e).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")) for e in range(-9, 0)}

# ------------------------------------------------------------------ authors
TITULO = ("CUDA: origen, arquitectura, modelo de programación y aplicaciones "
          "de la computación paralela en GPU")
AUTORES = [
    ("Heyley Yurani Parada Parada", "1093887319", "heyley.paradapar@unipamplona.edu.co"),
    ("Lisbeth Gissel Cordero Tovar", "1093293375", "lisbeth.corderotov@unipamplona.edu.co"),
]
AFILIACION = ["Programa de Ingeniería de Sistemas, Facultad de Ingenierías y Arquitectura",
              "Universidad de Pamplona, Villa del Rosario, Norte de Santander, Colombia"]

# ------------------------------------------------------------------ references
REFS = {
    "nvguide": 'NVIDIA Corporation, "CUDA C++ Programming Guide," Santa Clara, CA, USA, 2025. '
               '[Online]. Available: https://docs.nvidia.com/cuda/cuda-c-programming-guide/ (accedido: 23 nov. 2026).',
    "nickolls": 'J. Nickolls, I. Buck, M. Garland y K. Skadron, "Scalable parallel programming with CUDA," '
                '*ACM Queue*, vol. 6, no. 2, pp. 40–53, 2008, doi: 10.1145/1365490.1365500.',
    "owens2007": 'J. D. Owens, D. Luebke, N. Govindaraju, M. Harris, J. Krüger, A. E. Lefohn y T. J. Purcell, '
                 '"A survey of general-purpose computation on graphics hardware," *Comput. Graph. Forum*, '
                 'vol. 26, no. 1, pp. 80–113, 2007, doi: 10.1111/j.1467-8659.2007.01012.x.',
    "buck": 'I. Buck, T. Foley, D. Horn, J. Sugerman, K. Fatahalian, M. Houston y P. Hanrahan, '
            '"Brook for GPUs: Stream computing on graphics hardware," *ACM Trans. Graph.*, vol. 23, no. 3, '
            'pp. 777–786, 2004, doi: 10.1145/1015706.1015800.',
    "lindholm": 'E. Lindholm, J. Nickolls, S. Oberman y J. Montrym, "NVIDIA Tesla: A unified graphics and '
                'computing architecture," *IEEE Micro*, vol. 28, no. 2, pp. 39–55, 2008, doi: 10.1109/MM.2008.31.',
    "owens2008": 'J. D. Owens, M. Houston, D. Luebke, S. Green, J. E. Stone y J. C. Phillips, "GPU computing," '
                 '*Proc. IEEE*, vol. 96, no. 5, pp. 879–899, 2008, doi: 10.1109/JPROC.2008.917757.',
    "volta": 'J. Choquette, O. Giroux y D. Foley, "Volta: Performance and programmability," *IEEE Micro*, '
             'vol. 38, no. 2, pp. 42–52, 2018, doi: 10.1109/MM.2018.022071134.',
    "a100": 'J. Choquette, W. Gandhi, O. Giroux, N. Stam y R. Krashinsky, "NVIDIA A100 Tensor Core GPU: '
            'Performance and innovation," *IEEE Micro*, vol. 41, no. 2, pp. 29–35, 2021, doi: 10.1109/MM.2021.3061394.',
    "h100": 'J. Choquette, "NVIDIA Hopper H100 GPU: Scaling performance," *IEEE Micro*, vol. 43, no. 3, '
            'pp. 9–17, 2023, doi: 10.1109/MM.2023.3256796.',
    "amdahl": 'G. M. Amdahl, "Validity of the single processor approach to achieving large scale computing '
              'capabilities," en *Proc. AFIPS Spring Joint Comput. Conf.*, Atlantic City, NJ, USA, 1967, '
              'pp. 483–485, doi: 10.1145/1465482.1465560.',
    "hwu": 'W. W. Hwu, D. B. Kirk e I. El Hajj, *Programming Massively Parallel Processors: A Hands-on '
           'Approach*, 4.ª ed. Cambridge, MA, USA: Morgan Kaufmann, 2022.',
    "ptx": 'NVIDIA Corporation, "Parallel Thread Execution ISA," Santa Clara, CA, USA, 2025. [Online]. '
           'Available: https://docs.nvidia.com/cuda/parallel-thread-execution/ (accedido: 23 nov. 2026).',
    "sanders": 'J. Sanders y E. Kandrot, *CUDA by Example: An Introduction to General-Purpose GPU '
               'Programming*. Upper Saddle River, NJ, USA: Addison-Wesley, 2010.',
    "cudnn": 'S. Chetlur, C. Woolley, P. Vandermersch, J. Cohen, J. Tran, B. Catanzaro y E. Shelhamer, '
             '"cuDNN: Efficient primitives for deep learning," 2014, *arXiv:1410.0759*.',
    "numba": 'S. K. Lam, A. Pitrou y S. Seibert, "Numba: A LLVM-based Python JIT compiler," en *Proc. 2nd '
             'Workshop LLVM Compiler Infrastructure HPC (LLVM\'15)*, Austin, TX, USA, 2015, pp. 1–6, '
             'doi: 10.1145/2833157.2833162.',
    "ryoo": 'S. Ryoo, C. I. Rodrigues, S. S. Baghsorkhi, S. S. Stone, D. B. Kirk y W. W. Hwu, "Optimization '
            'principles and application performance evaluation of a multithreaded GPU using CUDA," en *Proc. '
            '13th ACM SIGPLAN Symp. Principles Practice Parallel Program. (PPoPP)*, Salt Lake City, UT, USA, '
            '2008, pp. 73–82, doi: 10.1145/1345206.1345220.',
    "opencl": 'J. E. Stone, D. Gohara y G. Shi, "OpenCL: A parallel programming standard for heterogeneous '
              'computing systems," *Comput. Sci. Eng.*, vol. 12, no. 3, pp. 66–73, 2010, doi: 10.1109/MCSE.2010.69.',
    "krizhevsky": 'A. Krizhevsky, I. Sutskever y G. E. Hinton, "ImageNet classification with deep '
                  'convolutional neural networks," en *Adv. Neural Inf. Process. Syst. (NeurIPS)*, vol. 25, '
                  '2012, pp. 1097–1105.',
    "anderson": 'J. A. Anderson, C. D. Lorenz y A. Travesset, "General purpose molecular dynamics simulations '
                'fully implemented on graphics processing units," *J. Comput. Phys.*, vol. 227, no. 10, '
                'pp. 5342–5359, 2008, doi: 10.1016/j.jcp.2008.01.047.',
    "eklund": 'A. Eklund, P. Dufort, D. Forsberg y S. M. LaConte, "Medical image processing on the GPU – '
              'Past, present and future," *Med. Image Anal.*, vol. 17, no. 8, pp. 1073–1094, 2013, '
              'doi: 10.1016/j.media.2013.05.008.',
    "volkov": 'V. Volkov y J. W. Demmel, "Benchmarking GPUs to tune dense linear algebra," en *Proc. '
              'ACM/IEEE Conf. Supercomputing (SC\'08)*, Austin, TX, USA, 2008, pp. 1–11, '
              'doi: 10.1109/SC.2008.5214359.',
    "bestpractices": 'NVIDIA Corporation, "CUDA C++ Best Practices Guide," Santa Clara, CA, USA, 2025. '
                     '[Online]. Available: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/ '
                     '(accedido: 23 nov. 2026).',
}

# ------------------------------------------------------------------ content
RESUMEN = (
    "CUDA (Compute Unified Device Architecture) es la plataforma de computación paralela y el modelo de "
    "programación con los que NVIDIA permite usar sus unidades de procesamiento gráfico (GPU) para cálculo de "
    "propósito general. Este informe describe su origen, desde la programación de GPU mediante shaders gráficos "
    "y el lenguaje Brook hasta su presentación en 2006 junto con la arquitectura Tesla; explica su modelo de "
    "ejecución heterogéneo, la jerarquía de hilos, bloques y mallas, la ejecución SIMT por warps y la jerarquía "
    "de memoria; resume su cadena de compilación, sus bibliotecas y sus herramientas, y analiza sus "
    "características, ventajas, desventajas, alternativas y casos de uso. Como caso práctico se midió una "
    "multiplicación de matrices de precisión simple en una GPU NVIDIA GeForce RTX 4050 Laptop con CUDA "
    f"{CUDA_VER}: con matrices de 2048 × 2048, un kernel básico fue {es(SP_NAIVE)} veces más rápido que un "
    f"núcleo de CPU, un kernel con memoria compartida {es(SP_TILED)} veces y la biblioteca cuBLAS "
    f"{es(SP_CUBLAS, 0)} veces. En cambio, en una suma de vectores la copia de datos por PCIe hizo que la GPU "
    "tardara más que la CPU. Se concluye que CUDA ofrece el ecosistema más maduro para el cómputo en GPU, a "
    "costa de depender de un solo fabricante, y que su beneficio depende de la intensidad aritmética del "
    "problema y del costo de mover los datos."
)
PALABRAS = ("CUDA, GPU, computación paralela, GPGPU, SIMT, jerarquía de memoria, cuBLAS, cuDNN, "
            "computación de alto rendimiento.")
ABSTRACT = (
    "CUDA (Compute Unified Device Architecture) is NVIDIA's parallel computing platform and programming model "
    "for general-purpose computing on its graphics processing units (GPUs). This report traces its origin, from "
    "shader-based GPU programming and the Brook language to its 2006 launch with the Tesla architecture; "
    "explains its heterogeneous execution model, the thread, block and grid hierarchy, SIMT execution in warps "
    "and the memory hierarchy; summarizes its toolchain, libraries and tools; and analyzes its features, "
    "advantages, drawbacks, alternatives and use cases. As a case study, single-precision matrix multiplication "
    f"was measured on an NVIDIA GeForce RTX 4050 Laptop GPU with CUDA {CUDA_VER}: for 2048 × 2048 matrices, a "
    f"basic kernel was {SP_NAIVE:.1f} times faster than one CPU core, a shared-memory kernel {SP_TILED:.1f} times "
    f"and cuBLAS {SP_CUBLAS:.0f} times, whereas for vector addition the PCIe transfers made the GPU slower than "
    "the CPU. CUDA offers the most mature GPU computing ecosystem at the cost of single-vendor lock-in, and its "
    "benefit depends on the arithmetic intensity of the problem and on the cost of moving data."
)
INDEX_TERMS = ("CUDA, GPU, parallel computing, GPGPU, SIMT, memory hierarchy, cuBLAS, cuDNN, "
               "high-performance computing.")

CODIGO = """__global__ void vecAdd(const float *a,
                       const float *b,
                       float *c, int n) {
  int i = blockIdx.x * blockDim.x
        + threadIdx.x;          // índice global
  if (i < n) c[i] = a[i] + b[i];
}

// Código del anfitrión (CPU)
cudaMalloc(&dA, bytes);   // ídem dB y dC
cudaMemcpy(dA, hA, bytes,
           cudaMemcpyHostToDevice);
int hilos  = 256;
int bloques = (n + hilos - 1) / hilos;
vecAdd<<<bloques, hilos>>>(dA, dB, dC, n);
cudaMemcpy(hC, dC, bytes,
           cudaMemcpyDeviceToHost);
cudaFree(dA);             // ídem dB y dC"""

TABLAS = {
    "arquitecturas": (
        "Evolución de las arquitecturas de GPU de NVIDIA compatibles con CUDA",
        ["Arquitectura", "Año", "CC", "Aporte principal para CUDA"],
        [("Tesla (G80)", "2006", "1.x", "Shaders unificados; primera GPU con CUDA"),
         ("Fermi", "2010", "2.x", "Cachés L1/L2, ECC y doble precisión rápida"),
         ("Kepler", "2012", "3.x", "Paralelismo dinámico y Hyper-Q"),
         ("Maxwell", "2014", "5.x", "Mejor rendimiento por vatio"),
         ("Pascal", "2016", "6.x", "NVLink, HBM2 y migración de páginas en memoria unificada"),
         ("Volta", "2017", "7.0", "Tensor Cores y planificación independiente de hilos"),
         ("Turing", "2018", "7.5", "RT Cores y Tensor Cores en GPU de consumo"),
         ("Ampere", "2020", "8.0/8.6", "TF32, dispersión estructurada y MIG"),
         ("Ada Lovelace", "2022", "8.9", "Tensor Cores de 4.ª generación con FP8"),
         ("Hopper", "2022", "9.0", "Transformer Engine, clústeres de bloques y TMA"),
         ("Blackwell", "2024", "10.x/12.x", "Tensor Cores de 5.ª generación con FP4")],
        [0.75, 0.38, 0.55, 1.62],
        "CC: capacidad de cómputo (compute capability) [[nvguide]], [[volta]], [[a100]], [[h100]].",
    ),
    "memorias": (
        "Espacios de memoria de CUDA",
        ["Memoria", "Ubicación", "Alcance", "Velocidad"],
        [("Registros", "En el chip (SM)", "Un hilo", "La más rápida"),
         ("Compartida", "En el chip (SM)", "Un bloque", "Muy alta"),
         ("Local", "DRAM, con caché", "Un hilo", "Baja"),
         ("Global", "DRAM (GDDR/HBM)", "Malla y CPU", "Baja, alto ancho de banda"),
         ("Constante (64 KB)", "DRAM, con caché", "Malla, solo lectura", "Alta si los hilos leen lo mismo"),
         ("Textura", "DRAM, con caché", "Malla, solo lectura", "Alta con localidad 2D")],
        [0.8, 0.85, 0.8, 0.85],
        "Fuente: [[nvguide]], [[hwu]].",
    ),
    "bibliotecas": (
        "Bibliotecas principales del ecosistema CUDA",
        ["Biblioteca", "Función"],
        [("cuBLAS", "Álgebra lineal densa (BLAS)"),
         ("cuFFT", "Transformada rápida de Fourier"),
         ("cuRAND", "Generación de números aleatorios"),
         ("cuSPARSE / cuSOLVER", "Matrices dispersas y solucionadores lineales"),
         ("cuDNN", "Primitivas de redes neuronales profundas"),
         ("TensorRT", "Optimización de la inferencia de redes neuronales"),
         ("NCCL", "Comunicación colectiva entre varias GPU"),
         ("Thrust / CUB", "Algoritmos paralelos genéricos en C++"),
         ("CUTLASS", "Plantillas C++ para GEMM de alto rendimiento")],
        [1.15, 2.15],
        "Fuente: documentación del CUDA Toolkit [[nvguide]] y [[cudnn]].",
    ),
    "alternativas": (
        "Comparación de CUDA con otras plataformas de cómputo en GPU",
        ["Plataforma", "Promotor", "Hardware", "Ventaja / limitación"],
        [("CUDA", "NVIDIA", "Solo GPU NVIDIA", "Ecosistema más maduro / un solo fabricante"),
         ("OpenCL", "Khronos Group", "CPU, GPU, FPGA", "Estándar abierto / API verbosa y soporte desigual"),
         ("HIP / ROCm", "AMD", "GPU AMD (y NVIDIA vía HIP)", "Sintaxis casi idéntica a CUDA / ecosistema menor"),
         ("SYCL / oneAPI", "Khronos / Intel", "CPU, GPU de varios fabricantes", "C++ estándar de fuente única / menos maduro"),
         ("OpenACC / OpenMP", "Consorcios abiertos", "Varios", "Directivas sobre código existente / menos control"),
         ("Metal", "Apple", "GPU Apple", "Integrado en macOS e iOS / solo ecosistema Apple")],
        [0.75, 0.7, 0.85, 1.0],
        "Fuente: [[opencl]], [[hwu]] y documentación de cada plataforma.",
    ),
    "equipo": (
        "Entorno del caso práctico",
        ["Elemento", "Valor"],
        [("GPU", f"{RES['gpu']} (CC {RES['compute_capability']})"),
         ("Multiprocesadores (SM)", f"{RES['sms']} SM, {CORES} núcleos CUDA"),
         ("Memoria de la GPU", f"{es(RES['global_mem_mib'] / 1024, 1)} GiB disponibles"),
         ("Memoria compartida", f"{RES['shared_mem_per_block_kib']} KiB por bloque; warp de {RES['warp_size']} hilos"),
         ("CPU", "AMD Ryzen 7 7435HS (8 núcleos, 16 hilos)"),
         ("Software", f"CUDA {CUDA_VER}, nvcc -O3 -arch=native, cuBLAS"),
         ("Repeticiones", f"{RES['reps']} por kernel tras un calentamiento")],
        [1.25, 2.05],
        "Datos leídos con cudaGetDeviceProperties en el propio equipo.",
    ),
}


def resultados_rows():
    rows = []
    for n in (512, 1024, 2048):
        r = MM[n]
        rows.append((f"{n}", es(r["cpu_ms"], 1), es(r["naive_ms"], 2), es(r["tiled_ms"], 2),
                     es(r["cublas_ms"], 2), es(r["h2d_ms"] + r["d2h_ms"], 2)))
    return rows


TABLAS["resultados"] = (
    "Tiempo medio de la multiplicación de matrices (ms)",
    ["N", "CPU", "Básico", "Comp.", "cuBLAS", "Copias"],
    resultados_rows(),
    [0.45, 0.6, 0.55, 0.55, 0.55, 0.6],
    "CPU: un hilo. Básico: kernel con memoria global. Comp.: kernel con memoria compartida. Copias: envío de "
    "A y B a la GPU y regreso de C. Los tiempos de la GPU no incluyen las copias.",
)

SECCIONES = [
    ("Introducción", [
        "Durante décadas el rendimiento de los programas secuenciales creció con la frecuencia de reloj de los "
        "procesadores. Cuando el consumo de energía y la disipación de calor frenaron ese crecimiento, la "
        "industria pasó a aumentar el número de núcleos, y el rendimiento quedó ligado a la capacidad de "
        "expresar el trabajo en paralelo [[hwu]]. Las unidades de procesamiento gráfico (GPU), diseñadas para "
        "calcular millones de píxeles a la vez, se convirtieron en el procesador paralelo más accesible.",
        "CUDA (Compute Unified Device Architecture) es la plataforma de NVIDIA que abrió ese hardware a la "
        "programación de propósito general con una extensión de C y C++ [[nvguide]], [[nickolls]]. Hoy está "
        "detrás del entrenamiento de casi todas las redes neuronales profundas, de buena parte de la simulación "
        "científica y de aplicaciones de imagen médica, finanzas y genómica.",
        "Este informe presenta CUDA de forma integral: la sección II narra su origen y evolución; la III "
        "compara la CPU con la GPU; la IV explica el modelo de programación y la jerarquía de memoria; la V "
        "describe la compilación y el ecosistema; las secciones VI a IX tratan las características, ventajas, "
        "desventajas y alternativas; la X reúne casos de uso, incluido el proyecto BioCafe de las autoras; la "
        "XI presenta un caso práctico medido en una GPU real; la XII resume buenas prácticas, la XIII las "
        "tendencias y la XIV las conclusiones.",
    ]),
    ("Origen y evolución de CUDA", [
        ("sub", "A. La computación de propósito general en GPU antes de CUDA"),
        "A comienzos de la década de 2000 las GPU incorporaron etapas programables, los shaders de vértices y "
        "de píxeles. Los investigadores descubrieron que, si codificaban sus datos como texturas y sus cálculos "
        "como operaciones de dibujo en OpenGL o DirectX, podían resolver problemas de álgebra lineal, "
        "simulación física o procesamiento de imágenes mucho más rápido que en la CPU. Esa práctica se llamó "
        "GPGPU (General-Purpose computing on GPU) [[owens2007]]. Su gran obstáculo era que obligaba a pensar "
        "cada algoritmo en términos de triángulos, texturas y píxeles, con precisión limitada y sin acceso "
        "arbitrario a la memoria.",
        "En 2004, un grupo de la Universidad de Stanford dirigido por Ian Buck presentó Brook for GPUs, un "
        "lenguaje de flujos (streams) que ocultaba la API gráfica y trataba la GPU como un coprocesador de "
        "datos en paralelo [[buck]]. Buck se unió después a NVIDIA, donde las ideas de Brook se convirtieron "
        "en la base de CUDA [[nickolls]].",
        ("sub", "B. El nacimiento de CUDA (2006–2007)"),
        "NVIDIA presentó CUDA en noviembre de 2006 junto con la GeForce 8800 GTX, basada en el chip G80 de la "
        "arquitectura Tesla. Fue la primera GPU de NVIDIA con shaders unificados: en lugar de unidades "
        "separadas para vértices y píxeles, tenía multiprocesadores de streaming (SM) formados por núcleos "
        "escalares intercambiables, aptos tanto para gráficos como para cómputo general [[lindholm]]. La "
        "primera versión pública del kit de desarrollo, CUDA 1.0, apareció en 2007. Por primera vez se podía "
        "programar una GPU en una variante de C, con punteros, memoria compartida explícita y sincronización "
        "entre hilos, sin pasar por la API gráfica [[nickolls]], [[owens2008]].",
        ("sub", "C. Evolución por arquitecturas"),
        "Desde entonces, cada generación de GPU agregó capacidades al modelo de programación, identificadas por "
        "la capacidad de cómputo (compute capability, CC) del dispositivo. La Tabla I resume las principales y "
        "la Fig. 1 ubica los hitos en el tiempo. Destacan la doble precisión y las cachés de Fermi, la memoria "
        "unificada de CUDA 6 (2014), los Tensor Cores de Volta, dedicados a multiplicar matrices pequeñas en "
        "precisión reducida para el aprendizaje profundo [[volta]], y las precisiones TF32, FP8 y FP4 de "
        "Ampere, Hopper y Blackwell [[a100]], [[h100]].",
        ("tabla", "arquitecturas"),
        ("fig", "linea_tiempo", "Línea de tiempo de los principales hitos de CUDA y del cómputo en GPU.", 3.2),
    ]),
    ("Fundamentos: CPU frente a GPU", [
        "Una CPU dedica gran parte de su área a la lógica de control (predicción de saltos, ejecución fuera de "
        "orden) y a cachés grandes, para que pocos hilos se ejecuten con la menor latencia posible. Una GPU "
        "dedica esa área a miles de unidades aritméticas sencillas y oculta la latencia de la memoria "
        "alternando entre muchos hilos: mientras un grupo espera datos, otro calcula (Fig. 2). La CPU está "
        "optimizada para la latencia; la GPU, para el rendimiento total (throughput) [[nvguide]], [[hwu]].",
        ("fig", "cpu_gpu", "Distribución del área del chip en una CPU y en una GPU (esquema adaptado de [[nvguide]]).", 3.2),
        "El beneficio de la GPU está acotado por la parte del programa que sigue siendo secuencial. La ley de "
        "Amdahl [[amdahl]] expresa la aceleración máxima S con N procesadores cuando una fracción p del tiempo "
        "es paralelizable:",
        ("ecuacion", "S(N) = 1 / [ (1 − p) + p / N ]", "1"),
        "Si el 95 % del programa es paralelo, la aceleración nunca superará 20 veces, por más núcleos que tenga "
        "la GPU. Por eso CUDA no reemplaza a la CPU: la complementa en un modelo heterogéneo en el que cada "
        "procesador hace lo que mejor sabe hacer.",
    ]),
    ("Arquitectura y modelo de programación", [
        ("sub", "A. Modelo heterogéneo: anfitrión y dispositivo"),
        "En CUDA, la CPU es el anfitrión (host) y la GPU el dispositivo (device), cada uno con su propia "
        "memoria. Un programa típico sigue los pasos de la Fig. 3: reserva memoria en la GPU, copia los datos "
        "de entrada, lanza un kernel (una función que se ejecuta en la GPU por miles de hilos a la vez), copia "
        "los resultados de regreso y libera la memoria [[nvguide]], [[sanders]]. La memoria unificada, "
        "disponible desde CUDA 6, permite usar un único puntero en ambos lados y deja que el sistema migre las "
        "páginas, aunque el costo físico del traslado sigue existiendo.",
        ("fig", "flujo", "Flujo de ejecución de un programa CUDA entre el anfitrión y el dispositivo.", 2.1),
        ("sub", "B. Jerarquía de hilos: mallas, bloques e hilos"),
        "Un kernel se lanza sobre una malla (grid) de bloques, y cada bloque contiene hasta "
        f"{RES['max_threads_per_block']} hilos organizados en una, dos o tres dimensiones (Fig. 4). Cada hilo "
        "conoce su posición mediante las variables integradas threadIdx, blockIdx, blockDim y gridDim, y con "
        "ellas calcula qué dato le corresponde. Los hilos de un mismo bloque se ejecutan en el mismo SM, pueden "
        "cooperar mediante memoria compartida y sincronizarse con __syncthreads(); los bloques, en cambio, son "
        "independientes entre sí. Esa independencia es la clave de la escalabilidad de CUDA: el mismo programa "
        "se reparte entre 2 o 200 SM sin modificarse [[nickolls]].",
        ("fig", "jerarquia", "Jerarquía de ejecución: una malla de bloques y un bloque de hilos.", 3.2),
        ("sub", "C. Ejecución SIMT y warps"),
        f"El SM agrupa los hilos de cada bloque en warps de {RES['warp_size']} hilos, que ejecutan la misma "
        "instrucción al mismo tiempo sobre datos distintos. NVIDIA llama a este modelo SIMT (Single Instruction, "
        "Multiple Threads) [[lindholm]]. Si los hilos de un warp toman caminos distintos en un if, el warp "
        "ejecuta ambos caminos uno tras otro y desactiva los hilos que no corresponden; esta divergencia reduce "
        "el rendimiento. Desde Volta, cada hilo tiene su propio contador de programa, lo que hace más segura la "
        "sincronización entre hilos de un mismo warp [[volta]]. La ocupación (occupancy), es decir, la "
        "proporción de warps activos frente al máximo del SM, determina cuánta latencia de memoria se puede "
        "ocultar.",
        ("sub", "D. Jerarquía de memoria"),
        "El rendimiento de un kernel suele depender más de cómo accede a la memoria que de cuántas operaciones "
        "realiza [[ryoo]]. CUDA expone varios espacios de memoria con distinto tamaño, alcance y velocidad "
        "(Tabla II y Fig. 5). Los registros y la memoria compartida están dentro del SM y son muy rápidos pero "
        "escasos; la memoria global reside en la DRAM de la tarjeta, es grande y tiene alto ancho de banda, "
        "pero una latencia de cientos de ciclos. Una regla central es la coalescencia: cuando los hilos "
        "consecutivos de un warp leen direcciones consecutivas, el hardware combina sus accesos en pocas "
        "transacciones [[bestpractices]].",
        ("tabla", "memorias"),
        ("fig", "memoria", "Jerarquía de memoria de una GPU con CUDA.", 2.6),
        ("sub", "E. Sincronización, streams y concurrencia"),
        "Los lanzamientos de kernels son asíncronos respecto a la CPU. Las operaciones se encolan en streams: "
        "las de un mismo stream se ejecutan en orden y las de streams distintos pueden solaparse, por ejemplo "
        "copiando un lote de datos mientras se procesa otro. Los eventos (cudaEvent) permiten medir tiempos y "
        "coordinar streams, y los grafos de CUDA (CUDA Graphs) registran una secuencia de operaciones para "
        "lanzarla de una sola vez con menos sobrecarga [[nvguide]]. Para sincronizar más allá de un bloque se "
        "usan operaciones atómicas o los grupos cooperativos (cooperative groups).",
        ("sub", "F. Ejemplo de kernel"),
        "El Listado 1 suma dos vectores. El calificador __global__ marca la función como kernel; cada hilo "
        "calcula su índice global y procesa un solo elemento. La sintaxis <<<bloques, hilos>>> indica la "
        "configuración de lanzamiento, y la condición i < n protege a los hilos sobrantes del último bloque.",
        ("codigo", "Listado 1. Suma de vectores en CUDA C++."),
    ]),
    ("Compilación y ecosistema", [
        ("sub", "A. Cadena de compilación"),
        "El compilador nvcc separa el código del anfitrión, que entrega al compilador de C++ del sistema (GCC, "
        "Clang o MSVC), del código del dispositivo (Fig. 6). Este último se traduce primero a PTX (Parallel "
        "Thread Execution), un lenguaje ensamblador virtual independiente de la generación de GPU [[ptx]], y "
        "luego a SASS, el código máquina de una arquitectura concreta. Ambos se empaquetan en un fatbinary "
        "dentro del ejecutable. Si la GPU donde se ejecuta el programa no tiene un SASS compatible, el "
        "controlador compila el PTX en tiempo de ejecución (JIT). Este diseño permite que programas antiguos "
        "funcionen en GPU nuevas.",
        ("fig", "compilacion", "Cadena de compilación de un programa CUDA con nvcc.", 2.3),
        ("sub", "B. Bibliotecas"),
        "Gran parte del valor de CUDA está en sus bibliotecas optimizadas por NVIDIA para cada arquitectura "
        "(Tabla III). Con ellas, un programador obtiene un rendimiento cercano al máximo del hardware sin "
        "escribir kernels; cuDNN, por ejemplo, es la base sobre la que los marcos de aprendizaje profundo "
        "ejecutan convoluciones en la GPU [[cudnn]].",
        ("tabla", "bibliotecas"),
        ("sub", "C. Lenguajes y herramientas"),
        "Además de C y C++, CUDA puede usarse desde Fortran (CUDA Fortran) y desde Python, con proyectos como "
        "Numba, que compila funciones de Python a kernels [[numba]], o CuPy, que reproduce la interfaz de NumPy "
        "en la GPU. Para depurar y optimizar, el CUDA Toolkit incluye Nsight Systems (línea de tiempo de todo "
        "el programa), Nsight Compute (análisis detallado de cada kernel), cuda-gdb y compute-sanitizer, que "
        "detecta accesos fuera de rango y condiciones de carrera.",
        ("sub", "D. Pila de software"),
        "La Fig. 7 resume cómo se apilan estas capas: las aplicaciones y los marcos de alto nivel se apoyan en "
        "las bibliotecas, estas en el runtime y el controlador de CUDA y, al final, en el hardware de la GPU.",
        ("fig", "pila", "Pila de software de CUDA.", 3.2),
    ]),
    ("Características principales", [
        ("lista", [
            "Extensión mínima de C y C++: calificadores (__global__, __device__, __shared__), variables "
            "integradas y la sintaxis de lanzamiento <<< >>> [[nvguide]].",
            "Modelo jerárquico de hilos, bloques y mallas que escala automáticamente con el número de SM.",
            "Memoria explícitamente gestionable, incluida la memoria compartida como caché controlada por el "
            "programador, y memoria unificada opcional.",
            "Compatibilidad hacia adelante gracias a PTX y a la compilación JIT del controlador [[ptx]].",
            "Ejecución asíncrona con streams, eventos y grafos para solapar cómputo y transferencias.",
            "Acceso a unidades especializadas como los Tensor Cores mediante bibliotecas o la API WMMA [[volta]].",
            "Soporte para varias GPU y varios nodos mediante NVLink, GPUDirect y NCCL.",
            "Kit de desarrollo gratuito para Linux y Windows, con documentación extensa.",
        ]),
    ]),
    ("Ventajas", [
        ("lista", [
            "Rendimiento: en problemas con mucho paralelismo de datos ofrece aceleraciones de uno o dos órdenes "
            "de magnitud frente a un núcleo de CPU, como muestra la sección XI [[volkov]].",
            "Madurez: casi dos décadas de desarrollo, con un ecosistema de bibliotecas, herramientas, libros y "
            "cursos sin equivalente en otras plataformas [[hwu]].",
            "Adopción: TensorFlow, PyTorch y la mayoría del software científico de alto rendimiento lo usan "
            "como plataforma principal.",
            "Curva de entrada moderada: quien conoce C puede escribir su primer kernel en poco tiempo, y quien "
            "solo usa Python aprovecha la GPU sin escribir código CUDA [[numba]].",
            "Escalabilidad: el mismo código funciona desde una GPU portátil hasta centros de datos con miles "
            "de GPU.",
            "Eficiencia energética: para cargas paralelas, la GPU hace más operaciones por vatio que la CPU.",
        ]),
    ]),
    ("Desventajas y limitaciones", [
        ("lista", [
            "Dependencia de un solo fabricante: CUDA solo funciona en GPU NVIDIA y su licencia es propietaria, "
            "lo que limita la portabilidad y el poder de negociación de quien la adopta.",
            "Costo de las transferencias: los datos deben viajar por PCIe entre la memoria de la CPU y la de la "
            "GPU; en problemas con poco cálculo por dato, la copia puede costar más que el cálculo (sección XI).",
            "Optimizar es difícil: alcanzar el máximo rendimiento exige entender coalescencia, ocupación, "
            "conflictos de bancos y divergencia [[ryoo]], [[bestpractices]].",
            "No todo se paraleliza: el código secuencial o con muchas dependencias se acelera poco (ley de "
            "Amdahl) [[amdahl]].",
            "Memoria limitada: la memoria de la GPU es mucho menor que la RAM de un servidor y obliga a "
            "particionar problemas grandes.",
            "Depuración más compleja: miles de hilos concurrentes hacen más difícil reproducir errores y "
            "condiciones de carrera.",
            "Compatibilidad de versiones: el controlador, el kit y la capacidad de cómputo deben coincidir, y "
            "las versiones nuevas retiran el soporte a arquitecturas antiguas.",
            "Costo y consumo del hardware: las GPU de centro de datos son caras y consumen cientos de vatios.",
        ]),
    ]),
    ("Comparación con otras plataformas", [
        "CUDA no es la única forma de programar GPU. OpenCL, estándar abierto del Khronos Group, funciona en "
        "hardware de varios fabricantes, pero su API es más verbosa y el soporte de cada fabricante es desigual "
        "[[opencl]]. HIP, de AMD, copia casi literalmente la sintaxis de CUDA para facilitar la migración a "
        "GPU AMD con ROCm. SYCL y oneAPI proponen C++ estándar de fuente única para varios dispositivos, y "
        "OpenACC y OpenMP permiten paralelizar código existente con directivas. La Tabla IV resume las "
        "diferencias. En la práctica, CUDA sigue siendo la referencia por la madurez de su ecosistema, y varias "
        "alternativas se definen por su compatibilidad con ella.",
        ("tabla", "alternativas"),
    ]),
    ("Casos de uso", [
        ("sub", "A. Inteligencia artificial y aprendizaje profundo"),
        "El caso de uso más influyente. En 2012, AlexNet se entrenó en dos GPU GeForce GTX 580 con CUDA y ganó "
        "el concurso ImageNet con una ventaja amplia, lo que marcó el inicio de la era del aprendizaje "
        "profundo [[krizhevsky]]. Desde entonces, entrenar e inferir redes neuronales, incluidos los grandes "
        "modelos de lenguaje, se hace casi siempre sobre CUDA, cuDNN y los Tensor Cores [[cudnn]], [[h100]].",
        ("sub", "B. Simulación científica e ingeniería"),
        "La dinámica molecular fue de las primeras áreas en adoptar CUDA: HOOMD-blue demostró en 2008 una "
        "simulación implementada por completo en la GPU [[anderson]], y paquetes como GROMACS, NAMD y AMBER "
        "aceleran hoy sus cálculos con CUDA. También se usa en dinámica de fluidos, clima, astrofísica y "
        "álgebra lineal densa [[volkov]], [[owens2008]].",
        ("sub", "C. Imagen médica"),
        "La reconstrucción de tomografías y resonancias, el registro y la segmentación de imágenes se benefician "
        "del paralelismo masivo, porque cada vóxel puede procesarse de forma casi independiente [[eklund]].",
        ("sub", "D. Otros dominios"),
        "Finanzas (simulación de Monte Carlo para valorar riesgos y derivados), bioinformática (alineamiento de "
        "secuencias y análisis genómico), visión por computador, procesamiento de video, criptografía y "
        "renderizado por trazado de rayos, que además usa los RT Cores de las arquitecturas recientes.",
        ("sub", "E. Caso de las autoras: el proyecto BioCafe"),
        "En el proyecto BioCafe, que clasifica fotos de hojas de café en cuatro clases (araña roja, minador, "
        "roya y sana), el modelo EfficientNet-B0 se entrenó con TensorFlow en GPU NVIDIA T4 de Google Colab, y "
        "la validación cruzada se ejecutó en un equipo local con GPU NVIDIA. En ambos casos TensorFlow delega "
        "las convoluciones en cuDNN, que se ejecuta sobre CUDA. La inferencia, en cambio, se ejecuta en el "
        "teléfono con TensorFlow Lite, sin GPU NVIDIA y sin conexión: CUDA acelera la etapa costosa de "
        "entrenar, y el modelo resultante funciona donde no hay GPU.",
    ]),
    ("Caso práctico: multiplicación de matrices en una GPU real", [
        ("sub", "A. Diseño del experimento"),
        "Para ilustrar con datos propios las ventajas y las limitaciones descritas, se programó en CUDA C++ la "
        "multiplicación C = A × B de matrices cuadradas de precisión simple, con N = 512, 1024 y 2048, en "
        "cuatro versiones: un bucle en un solo hilo de la CPU; un kernel básico en el que cada hilo calcula un "
        "elemento leyendo de la memoria global; un kernel por bloques (tiling) que carga submatrices de 32 × 32 "
        "en memoria compartida [[hwu]], y la rutina SGEMM de cuBLAS. Se midió también una suma de 2²⁴ "
        "elementos para observar el peso de las copias. Los tiempos de la GPU se midieron con eventos de CUDA "
        "como promedio de 10 ejecuciones, y cada resultado se comparó con el de la CPU: el error relativo "
        f"máximo fue del orden de 10{SUP[ERR_EXP]}, propio del orden distinto de las sumas en coma flotante. La Tabla V describe el equipo. El código y los resultados en bruto están "
        "en la carpeta experimento/ que acompaña este informe.",
        ("tabla", "equipo"),
        ("sub", "B. Resultados"),
        "La Tabla VI y la Fig. 8 muestran los resultados. Con N = 2048, la CPU tardó "
        f"{es(B['cpu_ms'], 0)} ms ({es(gflops(2048, B['cpu_ms']), 1)} GFLOP/s); el kernel básico, "
        f"{es(B['naive_ms'], 1)} ms ({es(SP_NAIVE, 1)} veces más rápido); el kernel con memoria compartida, "
        f"{es(B['tiled_ms'], 1)} ms ({es(SP_TILED, 1)} veces), y cuBLAS, {es(B['cublas_ms'], 2)} ms, equivalente "
        f"a {es(gflops(2048, B['cublas_ms']) / 1000, 2)} TFLOP/s y {es(SP_CUBLAS, 0)} veces más rápido. Aun "
        f"sumando las copias de ida y vuelta ({es(B['h2d_ms'] + B['d2h_ms'], 1)} ms), cuBLAS fue "
        f"{es(SP_CUBLAS_TOTAL, 0)} veces más rápido que la CPU.",
        ("tabla", "resultados"),
        ("fig", "rendimiento", "Rendimiento de la multiplicación de matrices (escala logarítmica).", 3.2),
        "La suma de vectores muestra el caso opuesto (Fig. 9). El kernel tardó solo "
        f"{es(VA['kernel_ms'], 2)} ms, pero enviar los dos vectores y traer el resultado costó "
        f"{es(VA['h2d_ms'] + VA['d2h_ms'], 1)} ms, el {es(VA_COPY_SHARE, 0)} % del total. Con "
        f"{es(VA_GPU_TOTAL, 1)} ms, la GPU fue más lenta que la CPU ({es(VA['cpu_ms'], 1)} ms).",
        ("fig", "vecadd", "Tiempo de la suma de 2²⁴ elementos en CPU y en GPU, separando las copias.", 3.2),
        ("sub", "C. Discusión"),
        "Los resultados confirman tres ideas de este informe. Primero, la intensidad aritmética decide: la "
        "multiplicación de matrices hace del orden de N operaciones por dato y amortiza las copias, mientras "
        "que la suma de vectores hace una sola y queda limitada por el bus PCIe. Segundo, la jerarquía de "
        "memoria importa: reutilizar datos en memoria compartida aceleró el kernel un "
        f"{es((B['naive_ms'] / B['tiled_ms'] - 1) * 100, 0)} % con N = 2048, aunque con N = 512 no hubo "
        "mejora, porque la caché L1 de la arquitectura Ada ya captura buena parte de la reutilización. "
        f"Tercero, las bibliotecas superan al código propio: cuBLAS fue {es(B['tiled_ms'] / B['cublas_ms'], 1)} "
        "veces más rápido que el kernel por bloques, porque usa registros, vectorización y ajustes específicos "
        "de cada arquitectura [[volkov]]. Como limitación, la referencia de CPU usa un solo hilo y no una "
        "biblioteca BLAS multihilo, que reduciría la diferencia; el objetivo era ilustrar el modelo de CUDA, "
        "no comparar procesadores.",
    ]),
    ("Buenas prácticas de optimización", [
        ("lista", [
            "Medir antes de optimizar, con Nsight Systems y Nsight Compute, y atacar primero el cuello de "
            "botella real [[bestpractices]].",
            "Minimizar las transferencias entre CPU y GPU, mantener los datos en la GPU entre kernels y usar "
            "memoria fijada (pinned) y streams para solapar copias y cómputo.",
            "Garantizar accesos coalescentes a la memoria global y reutilizar datos en memoria compartida.",
            "Elegir bloques con un múltiplo de 32 hilos y vigilar la ocupación, los registros por hilo y la "
            "memoria compartida por bloque.",
            "Evitar la divergencia dentro de los warps y los conflictos de bancos en memoria compartida.",
            "Preferir las bibliotecas (cuBLAS, cuDNN, Thrust) antes que escribir kernels propios.",
            "Comprobar siempre los códigos de error de la API y validar los resultados contra una versión de "
            "referencia.",
        ]),
    ]),
    ("Tendencias y perspectivas", [
        "La evolución reciente de CUDA está marcada por la inteligencia artificial: precisiones cada vez "
        "menores (FP8 y FP4) en los Tensor Cores, motores especializados para transformers y nuevas "
        "abstracciones como los clústeres de bloques y el acelerador de memoria TMA de Hopper [[h100]]. Crece "
        "también la programación desde Python, que acerca la GPU a científicos de datos sin experiencia en C++ "
        "[[numba]], y la integración de CPU y GPU en un mismo módulo con memoria coherente. En paralelo, la "
        "dependencia de un solo fabricante impulsa alternativas como ROCm/HIP, SYCL y compiladores que "
        "traducen código CUDA a otros dispositivos, por lo que la portabilidad será una cuestión central en "
        "los próximos años.",
    ]),
    ("Conclusiones", [
        "CUDA transformó la GPU de un acelerador gráfico en un procesador paralelo de propósito general. Su "
        "éxito se explica por la combinación de un modelo de programación sencillo, basado en C y C++ y en la "
        "jerarquía de hilos, bloques y mallas, con un hardware que evolucionó a su servicio y con un ecosistema "
        "de bibliotecas y herramientas que ninguna alternativa ha igualado.",
        "El caso práctico mostró, con mediciones propias, que la GPU puede ser cientos de veces más rápida que "
        "un núcleo de CPU en problemas con alta intensidad aritmética, que la jerarquía de memoria y las "
        "bibliotecas optimizadas marcan la diferencia, y que en problemas simples el costo de mover datos "
        "puede anular la ventaja. Usar CUDA con criterio exige, por tanto, analizar el problema antes de "
        "elegir la plataforma.",
        "Su principal desventaja es estratégica: atarse a un solo fabricante. Para proyectos académicos como "
        "BioCafe, en los que el entrenamiento se hace en la nube con GPU NVIDIA y la inferencia en el "
        "teléfono, CUDA es hoy la opción más práctica, siempre que el resultado final no dependa de ella.",
    ]),
]


# ------------------------------------------------------------------ figures
def dot_png(name, src):
    path = FIG / f"{name}.png"
    subprocess.run([DOT, "-Tpng", "-Gdpi=220", "-o", str(path)], input=src.encode(), check=True)
    return path


def fig_timeline():
    events = [
        ("2001", "Shaders programables en GPU de consumo"),
        ("2004", "Brook for GPUs (Stanford)"),
        ("2006", "Se anuncia CUDA con la GeForce 8800 (G80, Tesla)"),
        ("2007", "CUDA 1.0, primer kit de desarrollo público"),
        ("2010", "Fermi: ECC, cachés y doble precisión"),
        ("2012", "Kepler; AlexNet se entrena con CUDA"),
        ("2014", "CUDA 6: memoria unificada; cuDNN"),
        ("2016", "Pascal: NVLink y HBM2"),
        ("2017", "Volta: primeros Tensor Cores"),
        ("2020", "Ampere (A100): TF32 y MIG"),
        ("2022", "Hopper y Ada Lovelace; CUDA 12"),
        ("2024", "Blackwell: Tensor Cores con FP4"),
        ("2025", "Serie CUDA 13"),
    ]
    fig, ax = plt.subplots(figsize=(3.3, 3.9))
    ax.set_xlim(0, 10); ax.set_ylim(len(events) - 0.4, -0.6); ax.axis("off")
    ax.plot([1.55, 1.55], [-0.3, len(events) - 0.7], color=GREY, lw=1.2)
    for i, (y, t) in enumerate(events):
        key = y in ("2006", "2007")
        ax.scatter(1.55, i, s=38 if key else 22, color=GREEN if key else BLUE, zorder=3)
        ax.text(1.15, i, y, ha="right", va="center", fontsize=8, weight="bold")
        ax.text(1.95, i, t, ha="left", va="center", fontsize=7.4, weight="bold" if key else "normal")
    fig.tight_layout(pad=0.2)
    p = FIG / "linea_tiempo.png"; fig.savefig(p); plt.close(fig); return p


def fig_cpu_gpu():
    fig, axes = plt.subplots(1, 2, figsize=(3.3, 1.9))
    for ax, title in zip(axes, ("CPU", "GPU")):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
        ax.set_title(title, fontsize=9, weight="bold", pad=2)
    a = axes[0]
    a.add_patch(Rectangle((0.3, 6.0), 4.4, 3.6, fc="#FFD966", ec="k", lw=0.6))
    a.text(2.5, 7.8, "Control", ha="center", va="center", fontsize=7)
    for i, (x, y) in enumerate([(5.0, 7.9), (7.4, 7.9), (5.0, 6.0), (7.4, 6.0)]):
        a.add_patch(Rectangle((x, y), 2.2, 1.7, fc=GREEN, ec="k", lw=0.6))
        a.text(x + 1.1, y + 0.85, "ALU", ha="center", va="center", fontsize=6.5)
    a.add_patch(Rectangle((0.3, 2.4), 9.3, 3.3, fc="#9DC3E6", ec="k", lw=0.6))
    a.text(5, 4.05, "Caché (L1, L2, L3)", ha="center", va="center", fontsize=7)
    a.add_patch(Rectangle((0.3, 0.2), 9.3, 1.9, fc="#D9D9D9", ec="k", lw=0.6))
    a.text(5, 1.15, "DRAM", ha="center", va="center", fontsize=7)
    g = axes[1]
    for r in range(7):
        y = 9.4 - r * 1.0
        g.add_patch(Rectangle((0.3, y - 0.8), 0.6, 0.8, fc="#FFD966", ec="k", lw=0.4))
        g.add_patch(Rectangle((0.95, y - 0.8), 0.6, 0.8, fc="#9DC3E6", ec="k", lw=0.4))
        for c in range(12):
            g.add_patch(Rectangle((1.65 + c * 0.66, y - 0.8), 0.58, 0.8, fc=GREEN, ec="k", lw=0.3))
    g.add_patch(Rectangle((0.3, 1.9), 9.3, 0.7, fc="#9DC3E6", ec="k", lw=0.6))
    g.text(5, 2.25, "Caché L2", ha="center", va="center", fontsize=6.5)
    g.add_patch(Rectangle((0.3, 0.2), 9.3, 1.5, fc="#D9D9D9", ec="k", lw=0.6))
    g.text(5, 0.95, "DRAM (GDDR / HBM)", ha="center", va="center", fontsize=7)
    fig.text(0.5, 0.01, "Amarillo: control · Azul: caché · Verde: unidades aritméticas", ha="center", fontsize=6.3)
    fig.tight_layout(pad=0.3, rect=(0, 0.05, 1, 1))
    p = FIG / "cpu_gpu.png"; fig.savefig(p); plt.close(fig); return p


def fig_flujo():
    return dot_png("flujo", f"""
digraph G {{
  rankdir=TB; nodesep=0.25; ranksep=0.22;
  node [shape=box, style="rounded,filled", fontname="{GVF}", fontsize=11, width=2.8, height=0.42];
  edge [arrowsize=0.7, color="#404040"];
  subgraph cluster_h {{ label="Anfitrión (CPU)"; fontname="{GVF}"; fontsize=11; style="rounded"; color="#2F5597";
    a [label="1. Preparar datos en la RAM", fillcolor="#DEEBF7"];
    b [label="2. cudaMalloc: reservar memoria en la GPU", fillcolor="#DEEBF7"];
    c [label="3. cudaMemcpy: copiar entradas a la GPU", fillcolor="#DEEBF7"];
    d [label="4. Lanzar kernel<<<bloques, hilos>>>", fillcolor="#DEEBF7"];
  }}
  subgraph cluster_d {{ label="Dispositivo (GPU)"; fontname="{GVF}"; fontsize=11; style="rounded"; color="#4E7A00";
    e [label="5. Miles de hilos ejecutan el kernel", fillcolor="#E2F0C9"];
  }}
  subgraph cluster_h2 {{ label="Anfitrión (CPU)"; fontname="{GVF}"; fontsize=11; style="rounded"; color="#2F5597";
    f [label="6. cudaMemcpy: traer resultados", fillcolor="#DEEBF7"];
    g [label="7. cudaFree: liberar memoria", fillcolor="#DEEBF7"];
  }}
  a -> b -> c -> d -> e -> f -> g;
}}""")


def fig_jerarquia():
    fig, ax = plt.subplots(figsize=(3.3, 2.3))
    ax.set_xlim(0, 20); ax.set_ylim(0, 13); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.3, 4.6), 8.6, 7.6, boxstyle="round,pad=0.1", fc="#F2F2F2", ec="k", lw=0.7))
    ax.text(4.6, 12.55, "Malla (grid)", ha="center", fontsize=8, weight="bold")
    for r in range(2):
        for c in range(3):
            x, y = 0.8 + c * 2.75, 8.6 - r * 3.6
            hl = (r, c) == (1, 1)
            ax.add_patch(Rectangle((x, y), 2.45, 3.0, fc=GREEN if hl else "#C5E0B4", ec="k", lw=0.7 if not hl else 1.2))
            ax.text(x + 1.22, y + 1.5, f"Bloque\n({c},{r})", ha="center", va="center", fontsize=6.5)
    ax.add_patch(FancyBboxPatch((10.6, 4.6), 9.0, 7.6, boxstyle="round,pad=0.1", fc="#F2F2F2", ec="k", lw=0.7))
    ax.text(15.1, 12.55, "Bloque (1,1)", ha="center", fontsize=8, weight="bold")
    for r in range(3):
        for c in range(4):
            x, y = 11.0 + c * 2.15, 9.6 - r * 2.3
            ax.add_patch(Rectangle((x, y), 1.85, 1.9, fc="#DEEBF7", ec="k", lw=0.5))
            ax.text(x + 0.92, y + 0.95, f"Hilo\n({c},{r})", ha="center", va="center", fontsize=5.4)
    ax.add_patch(FancyArrowPatch((6.4, 6.6), (10.5, 8.4), arrowstyle="-|>", mutation_scale=9, color=ORANGE, lw=1.1))
    ax.text(10, 3.4, "kernel<<<dim3(3,2), dim3(4,3)>>>  →  6 bloques × 12 hilos = 72 hilos", ha="center", fontsize=6.8)
    ax.text(10, 1.9, "índice global x = blockIdx.x · blockDim.x + threadIdx.x", ha="center", fontsize=6.8, style="italic")
    ax.text(10, 0.5, "Los bloques se reparten entre los SM; cada bloque se divide en warps de 32 hilos.", ha="center", fontsize=6.3)
    fig.tight_layout(pad=0.1)
    p = FIG / "jerarquia.png"; fig.savefig(p); plt.close(fig); return p


def fig_memoria():
    return dot_png("memoria", f"""
digraph G {{
  rankdir=TB; nodesep=0.18; ranksep=0.3; compound=true;
  node [shape=box, style="rounded,filled", fontname="{GVF}", fontsize=10, height=0.36];
  edge [arrowsize=0.6, dir=both, color="#404040"];
  subgraph cluster_sm {{ label="Multiprocesador (SM), en el chip"; fontname="{GVF}"; fontsize=10; style=rounded; color="#4E7A00";
    t1 [label="Hilo", fillcolor="#FFFFFF", shape=ellipse]; t2 [label="Hilo", fillcolor="#FFFFFF", shape=ellipse];
    r1 [label="Registros", fillcolor="#C5E0B4"]; r2 [label="Registros", fillcolor="#C5E0B4"];
    sh [label="Memoria compartida / caché L1\\n(por bloque)", fillcolor="#A9D18E", width=2.6];
    t1 -> r1; t2 -> r2; r1 -> sh; r2 -> sh;
  }}
  l2 [label="Caché L2 (compartida por todos los SM)", fillcolor="#9DC3E6", width=2.9];
  subgraph cluster_dram {{ label="DRAM de la GPU (GDDR / HBM)"; fontname="{GVF}"; fontsize=10; style=rounded; color="#2F5597";
    gl [label="Global", fillcolor="#DEEBF7"]; lo [label="Local", fillcolor="#DEEBF7"];
    co [label="Constante", fillcolor="#DEEBF7"]; tx [label="Textura", fillcolor="#DEEBF7"];
  }}
  host [label="Memoria del anfitrión (RAM de la CPU)", fillcolor="#E7E6E6", width=2.9];
  sh -> l2; l2 -> co [lhead=cluster_dram];
  gl -> host [ltail=cluster_dram, label="  PCIe / NVLink", fontname="{GVF}", fontsize=9];
}}""")


def fig_compilacion():
    return dot_png("compilacion", f"""
digraph G {{
  rankdir=TB; nodesep=0.3; ranksep=0.22;
  node [shape=box, style="rounded,filled", fontname="{GVF}", fontsize=10, height=0.36];
  edge [arrowsize=0.6, color="#404040", fontname="{GVF}", fontsize=9];
  cu [label="programa.cu", fillcolor="#FFF2CC"];
  nv [label="nvcc (separa el código)", fillcolor="#E7E6E6"];
  hc [label="Código del anfitrión", fillcolor="#DEEBF7"];
  dc [label="Código del dispositivo", fillcolor="#E2F0C9"];
  cxx [label="GCC / Clang / MSVC", fillcolor="#DEEBF7"];
  ptx [label="PTX (ensamblador virtual)", fillcolor="#E2F0C9"];
  sass [label="SASS (código máquina, cubin)", fillcolor="#E2F0C9"];
  fat [label="fatbinary (PTX + SASS)", fillcolor="#C5E0B4"];
  ld [label="Enlazador", fillcolor="#E7E6E6"];
  exe [label="Ejecutable", fillcolor="#FFF2CC"];
  drv [label="Controlador: compila el PTX (JIT)\\nsi no hay SASS para la GPU", fillcolor="#FCE4D6"];
  cu -> nv; nv -> hc; nv -> dc; hc -> cxx; dc -> ptx; ptx -> sass [label=" ptxas"];
  ptx -> fat; sass -> fat; cxx -> ld; fat -> ld; ld -> exe; exe -> drv [style=dashed, label=" al ejecutar"];
}}""")


def fig_pila():
    layers = [
        ("Aplicaciones", "TensorFlow, PyTorch, GROMACS, BioCafe", "#FFF2CC"),
        ("Bibliotecas", "cuBLAS, cuDNN, cuFFT, NCCL, Thrust", "#C5E0B4"),
        ("Lenguajes", "CUDA C/C++, Fortran, Python", "#E2F0C9"),
        ("Runtime API", "cudaMalloc, cudaMemcpy, <<< >>>", "#DEEBF7"),
        ("Controlador", "Driver API, compilación JIT de PTX", "#BDD7EE"),
        ("GPU NVIDIA", "SM, núcleos CUDA, Tensor Cores", "#76B900"),
    ]
    fig, ax = plt.subplots(figsize=(3.3, 2.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, len(layers)); ax.axis("off")
    for i, (name, detail, c) in enumerate(layers):
        y = len(layers) - 1 - i
        fg = "white" if c == "#76B900" else "black"
        ax.add_patch(FancyBboxPatch((0.15, y + 0.08), 7.5, 0.82, boxstyle="round,pad=0.02", fc=c, ec="k", lw=0.6))
        ax.text(3.9, y + 0.62, name, ha="center", va="center", fontsize=7, weight="bold", color=fg)
        ax.text(3.9, y + 0.32, detail, ha="center", va="center", fontsize=6.2, color=fg)
    ax.add_patch(FancyBboxPatch((7.95, 1.1), 1.9, 3.8, boxstyle="round,pad=0.02", fc="#FCE4D6", ec="k", lw=0.6))
    ax.text(8.9, 4.5, "Herramientas", ha="center", va="center", fontsize=6.3, weight="bold")
    ax.text(8.9, 2.8, "Nsight\nSystems\n\nNsight\nCompute\n\ncuda-gdb\n\ncompute-\nsanitizer",
            ha="center", va="center", fontsize=6)
    fig.tight_layout(pad=0.1)
    p = FIG / "pila.png"; fig.savefig(p); plt.close(fig); return p


def fig_rendimiento():
    ns = [512, 1024, 2048]
    series = [("CPU (1 hilo)", "cpu_ms", GREY), ("Kernel básico", "naive_ms", BLUE),
              ("Memoria compartida", "tiled_ms", ORANGE), ("cuBLAS", "cublas_ms", GREEN)]
    fig, ax = plt.subplots(figsize=(3.3, 2.2))
    w = 0.2
    for k, (lab, key, col) in enumerate(series):
        vals = [gflops(n, MM[n][key]) for n in ns]
        xs = [i + (k - 1.5) * w for i in range(3)]
        bars = ax.bar(xs, vals, w, label=lab, color=col, edgecolor="k", linewidth=0.3)
        for x, v in zip(xs, vals):
            ax.text(x, v * 1.12, f"{v:,.0f}".replace(",", "."), ha="center", va="bottom", fontsize=5, rotation=90)
    ax.set_yscale("log"); ax.set_ylim(5, 60000)
    ax.set_xticks(range(3)); ax.set_xticklabels([f"N = {n}" for n in ns])
    ax.set_ylabel("GFLOP/s (escala log.)")
    ax.legend(fontsize=6, ncol=2, loc="upper left", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.3)
    p = FIG / "rendimiento.png"; fig.savefig(p); plt.close(fig); return p


def fig_vecadd():
    fig, ax = plt.subplots(figsize=(3.3, 1.35))
    ax.barh(1, VA["cpu_ms"], color=GREY, edgecolor="k", lw=0.3, label="Cálculo en CPU")
    left = 0
    for v, lab, col in ((VA["h2d_ms"], "Copia CPU → GPU", "#9DC3E6"), (VA["kernel_ms"], "Kernel", GREEN),
                        (VA["d2h_ms"], "Copia GPU → CPU", BLUE)):
        ax.barh(0, v, left=left, color=col, edgecolor="k", lw=0.3, label=lab); left += v
    ax.text(VA["cpu_ms"] + 0.3, 1, f"{es(VA['cpu_ms'], 1)} ms", va="center", fontsize=6.5)
    ax.text(left + 0.3, 0, f"{es(left, 1)} ms", va="center", fontsize=6.5)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["GPU", "CPU"]); ax.set_xlabel("Tiempo (ms)")
    ax.set_xlim(0, left * 1.22)
    ax.legend(fontsize=5.6, ncol=2, loc="lower right", bbox_to_anchor=(1.0, 1.0), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.3)
    p = FIG / "vecadd.png"; fig.savefig(p); plt.close(fig); return p


# ------------------------------------------------------------------ citations
def citation_order():
    order = []

    def scan(t):
        for k in re.findall(r"\[\[(\w+)\]\]", t):
            if k not in REFS:
                raise KeyError(f"unknown reference {k}")
            if k not in order:
                order.append(k)

    for _, blocks in SECCIONES:
        for b in blocks:
            if isinstance(b, str):
                scan(b)
            elif b[0] == "lista":
                for it in b[1]: scan(it)
            elif b[0] == "fig":
                scan(b[2])
            elif b[0] == "tabla":
                scan(TABLAS[b[1]][4])
    missing = set(REFS) - set(order)
    if missing:
        raise ValueError(f"references never cited: {missing}")
    return order


ORDER = citation_order()
NUM = {k: i + 1 for i, k in enumerate(ORDER)}


def cite(t):
    return re.sub(r"\[\[(\w+)\]\]", lambda m: f"[{NUM[m.group(1)]}]", t)


# ------------------------------------------------------------------ docx helpers
def set_font(run, size=None, bold=None, italic=None, small_caps=None, font=FONT):
    run.font.name = font
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), font)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic
    if small_caps is not None: run.font.small_caps = small_caps


def para(doc, text="", size=10, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=None, before=0, after=0, keep=False, **fmt):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.0
    if indent is not None: pf.first_line_indent = Inches(indent)
    if keep: pf.keep_with_next = True
    if text: set_font(p.add_run(text), size, **fmt)
    return p


def rich(p, text, size):
    """Add text where *...* is italic (journal and book titles)."""
    for i, chunk in enumerate(re.split(r"\*", text)):
        if chunk: set_font(p.add_run(chunk), size, italic=(i % 2 == 1))


def hyperlink(p, url, text, size):
    r_id = p.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    run = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    f = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): f.set(qn(a), FONT)
    rpr.append(f)
    for tag, val in (("w:color", "1F4E99"), ("w:u", "single"), ("w:sz", str(int(size * 2)))):
        e = OxmlElement(tag); e.set(qn("w:val"), val); rpr.append(e)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve")
    run.append(rpr); run.append(t); h.append(run); p._p.append(h)


def page_setup(section):
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.orientation = WD_ORIENT.PORTRAIT
    section.top_margin, section.bottom_margin = Inches(0.75), Inches(1.0)
    section.left_margin = section.right_margin = Inches(0.625)


def set_columns(section, num, space=0.25):
    cols = section._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols"); section._sectPr.append(cols)
    cols.set(qn("w:num"), str(num)); cols.set(qn("w:space"), str(int(space * 1440)))


def page_number_footer(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(); set_font(run, 8)
    for kind, text in (("begin", None), (None, "PAGE"), ("separate", None), (None, "1"), ("end", None)):
        if kind:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), kind); run._r.append(e)
        elif text == "PAGE":
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = " PAGE "; run._r.append(e)
        else:
            e = OxmlElement("w:t"); e.text = text; run._r.append(e)


def shade(el_pr, fill):
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    el_pr.append(shd)


def add_table(doc, header, rows, widths, size=7):
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = OxmlElement("w:tblHeader"); hdr.set(qn("w:val"), "true"); t.rows[0]._tr.get_or_add_trPr().append(hdr)
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; shade(c._tc.get_or_add_tcPr(), "D9E2F3")
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; set_font(p.add_run(h), size, bold=True)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 or not re.match(r"^[\d.,]+$", str(v)) else WD_ALIGN_PARAGRAPH.CENTER
            set_font(p.add_run(str(v)), size)
    layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(layout)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    for i, w in enumerate(widths): t.columns[i].width = Inches(w)
    return t


# ------------------------------------------------------------------ build
def build():
    FIG.mkdir(exist_ok=True)
    figs = {"linea_tiempo": fig_timeline(), "cpu_gpu": fig_cpu_gpu(), "flujo": fig_flujo(),
            "jerarquia": fig_jerarquia(), "memoria": fig_memoria(), "compilacion": fig_compilacion(),
            "pila": fig_pila(), "rendimiento": fig_rendimiento(), "vecadd": fig_vecadd()}

    doc = Document()
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    doc.core_properties.title = TITULO
    doc.core_properties.author = "; ".join(a[0] for a in AUTORES)
    doc.core_properties.language = "es-CO"
    s0 = doc.sections[0]; page_setup(s0); page_number_footer(s0)

    para(doc, TITULO, 22, WD_ALIGN_PARAGRAPH.CENTER, after=12)
    for name, cc, mail in AUTORES:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_font(p.add_run(name), 11); set_font(p.add_run(f"  ·  C.C. {cc}"), 9)
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, after=3); hyperlink(p, "mailto:" + mail, mail, 9)
    para(doc, after=2)
    for line in AFILIACION:
        para(doc, line, 10, WD_ALIGN_PARAGRAPH.CENTER, italic=True)
    para(doc, after=8)

    body = doc.add_section(WD_SECTION.CONTINUOUS); page_setup(body); set_columns(body, 2)

    def labeled(label, text):
        p = para(doc, after=5)
        set_font(p.add_run(label), 9, bold=True, italic=True); set_font(p.add_run(text), 9, bold=True)

    labeled("Resumen—", RESUMEN)
    labeled("Palabras clave—", PALABRAS)
    labeled("Abstract—", ABSTRACT)
    labeled("Index Terms—", INDEX_TERMS)

    fig_n = tab_n = 0
    for si, (title, blocks) in enumerate(SECCIONES):
        para(doc, f"{ROMAN[si]}. {title}", 10, WD_ALIGN_PARAGRAPH.CENTER, before=8, after=4, keep=True, small_caps=True)
        for b in blocks:
            if isinstance(b, str):
                para(doc, cite(b), 10, indent=0.15, after=2)
            elif b[0] == "sub":
                para(doc, b[1], 10, WD_ALIGN_PARAGRAPH.LEFT, before=4, after=2, keep=True, italic=True)
            elif b[0] == "lista":
                for it in b[1]:
                    p = para(doc, after=2)
                    p.paragraph_format.left_indent = Inches(0.2); p.paragraph_format.first_line_indent = Inches(-0.13)
                    set_font(p.add_run("•\u00a0\u00a0" + cite(it)), 10)
            elif b[0] == "ecuacion":
                p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=3, after=3)
                set_font(p.add_run(b[1]), 10, italic=True); set_font(p.add_run(f"\t\t({b[2]})"), 10)
            elif b[0] == "codigo":
                para(doc, b[1], 8, WD_ALIGN_PARAGRAPH.LEFT, before=4, after=2, keep=True)
                lines = CODIGO.split("\n")
                for i, line in enumerate(lines):
                    p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, keep=i < len(lines) - 1)
                    shade(p._p.get_or_add_pPr(), "F2F2F2")
                    set_font(p.add_run(line if line else " "), 7.5, font=MONO)
                para(doc, after=4)
            elif b[0] == "fig":
                fig_n += 1
                p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, keep=True)
                p.add_run().add_picture(str(figs[b[1]]), width=Inches(b[3]))
                para(doc, cite(f"Fig. {fig_n}. {b[2]}"), 8, WD_ALIGN_PARAGRAPH.CENTER, before=2, after=8)
            elif b[0] == "tabla":
                tab_n += 1
                title_t, header, rows, widths, note = TABLAS[b[1]]
                para(doc, f"Tabla {ROMAN[tab_n - 1]}", 8, WD_ALIGN_PARAGRAPH.CENTER, before=6, keep=True, small_caps=True)
                para(doc, title_t, 8, WD_ALIGN_PARAGRAPH.CENTER, after=3, keep=True, small_caps=True)
                add_table(doc, header, rows, widths)
                para(doc, cite(note), 7, WD_ALIGN_PARAGRAPH.LEFT, before=2, after=8)

    para(doc, "Referencias", 10, WD_ALIGN_PARAGRAPH.CENTER, before=8, after=4, keep=True, small_caps=True)
    for k in ORDER:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, after=1)
        p.paragraph_format.left_indent = Inches(0.3); p.paragraph_format.first_line_indent = Inches(-0.3)
        set_font(p.add_run(f"[{NUM[k]}]\t"), 8)
        text = REFS[k]
        m = re.search(r"doi: (\S+)\.$", text)
        url = re.search(r"Available: (\S+)", text)
        if m:
            rich(p, text[: m.start()] + "doi: ", 8); hyperlink(p, "https://doi.org/" + m.group(1), m.group(1), 8)
            set_font(p.add_run("."), 8)
        elif url:
            rich(p, text[: url.start(1)], 8); hyperlink(p, url.group(1), url.group(1), 8)
            rich(p, text[url.end(1):], 8)
        else:
            rich(p, text, 8)
    doc.save(OUT)
    print(f"{OUT.name}: {len(SECCIONES)} secciones, {fig_n} figuras, {tab_n} tablas, {len(ORDER)} referencias")


if __name__ == "__main__":
    build()
