import { Camera, Cpu, ClipboardList } from 'lucide-react'
import { Group, GroupRow, Section } from './section'
import { PhoneFrame } from './phone-frame'

const steps = [
  {
    icon: Camera,
    text: 'Toma una foto de una hoja o elígela de la galería.',
  },
  {
    icon: Cpu,
    text: 'El modelo la analiza en el teléfono, sin enviar nada a internet.',
  },
  {
    icon: ClipboardList,
    text: 'Muestra la clase más probable, la confianza y una ficha informativa.',
  },
]

export function HowItWorks() {
  return (
    <div className="grid items-center gap-12 lg:grid-cols-[auto_minmax(0,1fr)] lg:gap-20">
      <PhoneFrame
        src="/app-resultado.png"
        alt="Captura de la pantalla de resultado de la app, con la clase detectada, la confianza y la ficha informativa."
        className="order-last mx-auto lg:order-none"
      />
      <Section id="como-funciona" title="Cómo funciona">
        <Group as="ol">
          {steps.map(({ icon: Icon, text }, i) => (
            <GroupRow
              key={text}
              first={i === 0}
              leading={
                <span className="flex size-9 items-center justify-center rounded-[10px] bg-secondary text-secondary-foreground">
                  <Icon className="size-5" aria-hidden="true" />
                </span>
              }
            >
              {text}
            </GroupRow>
          ))}
        </Group>
      </Section>
    </div>
  )
}
