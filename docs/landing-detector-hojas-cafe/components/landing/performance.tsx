import { Group, Section } from './section'

const metrics = [
  {
    value: '99 %',
    text: 'de exactitud en imágenes de los mismos conjuntos con que se entrenó.',
  },
  {
    value: '80 %',
    text: 'de exactitud en un conjunto externo que el modelo nunca vio.',
  },
]

export function Performance() {
  return (
    <Section id="que-tan-bien-funciona" title="Qué tan bien funciona">
      <Group as="div" className="grid sm:grid-cols-2">
        {metrics.map(({ value, text }, i) => (
          <div
            key={value}
            className={
              i === 0
                ? 'flex flex-col gap-2 p-5'
                : 'flex flex-col gap-2 border-t border-separator p-5 sm:border-t-0 sm:border-l'
            }
          >
            <p className="text-5xl leading-none font-bold tracking-[-0.03em] text-tint tabular-nums">
              {value}
            </p>
            <p className="leading-normal text-pretty text-muted-foreground">{text}</p>
          </div>
        ))}
      </Group>
      <p className="px-4 leading-relaxed text-pretty text-muted-foreground">
        La segunda cifra es la que mejor estima el uso real. El modelo confunde con frecuencia el
        minador con la roya, y no se ha evaluado con fotos de campo en Colombia.
      </p>
    </Section>
  )
}
