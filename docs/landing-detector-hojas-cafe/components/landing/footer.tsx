const datasets = [
  'RoCoLe (Parraga-Alava et al., 2019)',
  'DECAFIA (Rosas Ruiz, Salom Medina y Barrero Perez, 2026)',
  'BRACOL (Krohling, Esgario y Ventura, 2019)',
  'JMuBEN (2021)',
  'Silva et al. (2020)',
]

export function Footer() {
  return (
    <footer className="border-t border-separator">
      <div className="mx-auto grid w-full max-w-5xl gap-8 px-5 py-10 text-sm leading-relaxed text-muted-foreground sm:px-8 lg:grid-cols-2 lg:gap-10">
        <p className="max-w-md text-pretty">
          Proyecto Sistema de Detección Temprana de Plagas y Enfermedades en Cultivos de Café ·
          FCPD 2026-2 · Universidad de Pamplona
        </p>
        <div className="flex flex-col gap-2">
          <p className="font-medium text-foreground">Créditos de datos (licencia CC BY 4.0)</p>
          <ul className="flex flex-col gap-1">
            {datasets.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </div>
      </div>
    </footer>
  )
}
