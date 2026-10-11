export type Screen =
  | 'home'
  | 'camera'
  | 'camera-denied'
  | 'result-ok'
  | 'result-low'

export const CLASSES = [
  'Hoja sana',
  'Roya del café',
  'Minador de las hojas',
  'Mancha de hierro',
] as const

export type ClassName = (typeof CLASSES)[number]

export const SAMPLE_PHOTO = '/images/hoja-cafe.png'

export const ACCEPTED_RESULT = {
  label: 'Roya del café' as ClassName,
  confidence: 0.91,
  top3: [
    { label: 'Roya del café' as ClassName, confidence: 0.91 },
    { label: 'Mancha de hierro' as ClassName, confidence: 0.06 },
    { label: 'Hoja sana' as ClassName, confidence: 0.02 },
  ],
  symptoms:
    'Manchas amarillas o anaranjadas en el envés de la hoja, con aspecto polvoriento. Con el tiempo las zonas afectadas se oscurecen y la hoja puede caer.',
  conditions:
    'Humedad relativa alta, temperaturas templadas y periodos prolongados de hoja mojada. Las plantaciones densas y con poca ventilación son más susceptibles.',
}

export const LOW_CONFIDENCE_RESULT = {
  confidence: 0.38,
  tips: [
    'Acerca la cámara: la hoja debe ocupar la mayor parte del marco.',
    'Usa luz natural, sin sombras fuertes ni reflejos.',
    'Coloca la hoja sobre un fondo liso y de un solo color.',
    'Sujeta el teléfono firme para evitar fotos borrosas.',
  ],
}

export const ABOUT = {
  modelVersion: 'v0.3.1 (MobileNetV3, 2026-09)',
  datasets: [
    { name: 'BRACOL – Brazilian Arabica Coffee Leaf', detail: 'Krohling et al.' },
    { name: 'RoCoLe – Robusta Coffee Leaf', detail: 'Parraga-Alava et al.' },
    { name: 'Fotos propias de campo', detail: 'Proyecto académico, 2026' },
  ],
}
