import { Minus } from 'lucide-react'
import { Group, GroupRow, Section } from './section'

const items = [
  'Solo reconoce cuatro clases: hoja sana, roya, minador y arañita roja.',
  'La arañita roja es la clase menos fiable: se entrenó con imágenes de una sola fuente y en la prueba acertó 13 de 22.',
  'Cuando el modelo duda entre arañita roja y roya, la app muestra las dos posibilidades en lugar de elegir una.',
  'Solo conoce hojas: si la foto no es una hoja, igual dará una respuesta.',
  'No da recomendaciones de tratamiento.',
]

export function Limitations() {
  return (
    <Section id="limitaciones" title="Limitaciones">
      <Group>
        {items.map((text, i) => (
          <GroupRow
            key={text}
            first={i === 0}
            leading={<Minus className="size-5 text-tint" aria-hidden="true" />}
          >
            {text}
          </GroupRow>
        ))}
      </Group>
    </Section>
  )
}
