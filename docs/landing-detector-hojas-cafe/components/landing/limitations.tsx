import { Minus } from 'lucide-react'
import { Group, GroupRow, Section } from './section'

const items = [
  'Solo reconoce tres clases: hoja sana, roya y minador.',
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
