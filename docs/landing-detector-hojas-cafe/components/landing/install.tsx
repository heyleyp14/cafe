import { Group, GroupRow, Section } from './section'

const steps = [
  'Descarga el archivo APK en tu teléfono Android.',
  'Ábrelo y, si el teléfono lo pide, permite instalar apps de este origen.',
  'Abre la app y concede el permiso de cámara.',
]

export function Install() {
  return (
    <Section id="como-instalarla" title="Cómo instalarla">
      <Group as="ol">
        {steps.map((text, i) => (
          <GroupRow
            key={text}
            first={i === 0}
            leading={
              <span className="flex size-9 items-center justify-center rounded-full bg-primary text-[15px] font-bold text-primary-foreground tabular-nums">
                {i + 1}
              </span>
            }
          >
            {text}
          </GroupRow>
        ))}
      </Group>
    </Section>
  )
}
