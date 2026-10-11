import Image from 'next/image'
import { ChevronLeft, Camera, HelpCircle, CheckCircle2 } from 'lucide-react'
import {
  ACCEPTED_RESULT,
  LOW_CONFIDENCE_RESULT,
  SAMPLE_PHOTO,
} from '@/lib/mock-data'
import { IosButton } from '@/components/ios-button'

type ResultProps = {
  onBack: () => void
  onNewPhoto: () => void
}

export function ResultAcceptedScreen({ onBack, onNewPhoto }: ResultProps) {
  const pct = Math.round(ACCEPTED_RESULT.confidence * 100)

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <NavBar title="Resultado" onBack={onBack} />

      <main className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-4 pb-4 pt-2">
        <section aria-labelledby="clase" className="flex flex-col gap-2">
          <div className="flex gap-4 rounded-xl bg-surface-low p-4">
            <Image
              src={SAMPLE_PHOTO}
              alt="Miniatura de la hoja analizada"
              width={80}
              height={80}
              className="size-20 shrink-0 rounded-lg object-cover"
            />
            <div className="flex min-w-0 flex-1 flex-col justify-center gap-0.5">
              <p className="flex items-center gap-1 text-[13px] font-medium text-primary">
                <CheckCircle2 className="size-4" aria-hidden="true" />
                Clase detectada
              </p>
              <h1 id="clase" className="text-[22px] font-bold leading-tight tracking-tight">
                {ACCEPTED_RESULT.label}
              </h1>
              <div className="mt-1.5">
                <div className="flex items-baseline justify-between text-[13px] text-muted-foreground">
                  <span>Confianza</span>
                  <span className="text-[15px] font-semibold text-foreground tabular-nums">
                    {pct}%
                  </span>
                </div>
                <div
                  role="progressbar"
                  aria-label="Confianza del modelo"
                  aria-valuenow={pct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  className="mt-1 h-1 overflow-hidden rounded-full bg-fill"
                >
                  <div className="h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section aria-labelledby="top3" className="flex flex-col gap-2">
          <h2 id="top3" className="px-4 text-[13px] uppercase tracking-wide text-muted-foreground">
            Clases más probables
          </h2>
          <ol className="overflow-hidden rounded-xl bg-surface-low pl-4">
            {ACCEPTED_RESULT.top3.map((item, i) => {
              const p = Math.round(item.confidence * 100)
              return (
                <li
                  key={item.label}
                  className={`flex flex-col gap-1.5 py-2.5 pr-4 ${
                    i < ACCEPTED_RESULT.top3.length - 1 ? 'border-b border-separator' : ''
                  }`}
                >
                  <div className="flex items-baseline justify-between text-[17px]">
                    <span>{item.label}</span>
                    <span className="text-muted-foreground tabular-nums">{p}%</span>
                  </div>
                  <div aria-hidden="true" className="h-1 overflow-hidden rounded-full bg-fill">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${Math.max(p, 2)}%` }}
                    />
                  </div>
                </li>
              )
            })}
          </ol>
        </section>

        <section aria-labelledby="ficha" className="flex flex-col gap-2">
          <h2 id="ficha" className="px-4 text-[13px] uppercase tracking-wide text-muted-foreground">
            Ficha · {ACCEPTED_RESULT.label}
          </h2>
          <div className="rounded-xl bg-surface-low pl-4">
            <div className="border-b border-separator py-3 pr-4">
              <h3 className="text-[17px] font-semibold">Síntomas</h3>
              <p className="mt-1 text-[15px] leading-relaxed text-muted-foreground">
                {ACCEPTED_RESULT.symptoms}
              </p>
            </div>
            <div className="py-3 pr-4">
              <h3 className="text-[17px] font-semibold">Condiciones favorables</h3>
              <p className="mt-1 text-[15px] leading-relaxed text-muted-foreground">
                {ACCEPTED_RESULT.conditions}
              </p>
            </div>
          </div>
          <p className="px-4 text-[13px] leading-relaxed text-muted-foreground">
            Prototipo académico de apoyo. No es una herramienta de diagnóstico.
          </p>
        </section>
      </main>

      <footer className="border-t border-separator bg-background/90 px-4 pb-3 pt-3 backdrop-blur-xl">
        <IosButton onClick={onNewPhoto} icon={<Camera className="size-5" />}>
          Nueva foto
        </IosButton>
      </footer>
    </div>
  )
}

export function ResultLowConfidenceScreen({ onBack, onNewPhoto }: ResultProps) {
  const pct = Math.round(LOW_CONFIDENCE_RESULT.confidence * 100)

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <NavBar title="Resultado" onBack={onBack} />

      <main className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-4 pb-2 pt-2">
        <section className="flex flex-col items-center gap-3 px-4 pt-6 text-center">
          <HelpCircle className="size-14 text-muted-foreground" aria-hidden="true" strokeWidth={1.5} />
          <h1 className="text-[22px] font-bold leading-tight tracking-tight text-balance">
            No se pudo determinar con seguridad
          </h1>
          <p className="text-[15px] leading-relaxed text-muted-foreground text-pretty">
            La confianza del modelo fue de {pct}%, por debajo del mínimo requerido para
            mostrar un resultado.
          </p>
        </section>

        <section aria-labelledby="consejos" className="flex flex-col gap-2">
          <h2 id="consejos" className="px-4 text-[13px] uppercase tracking-wide text-muted-foreground">
            Consejos para la próxima captura
          </h2>
          <ul className="overflow-hidden rounded-xl bg-surface-low pl-4">
            {LOW_CONFIDENCE_RESULT.tips.map((tip, i) => (
              <li
                key={tip}
                className={`py-3 pr-4 text-[17px] leading-snug ${
                  i < LOW_CONFIDENCE_RESULT.tips.length - 1 ? 'border-b border-separator' : ''
                }`}
              >
                {tip}
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="border-t border-separator bg-background/90 px-4 pb-3 pt-3 backdrop-blur-xl">
        <IosButton onClick={onNewPhoto} icon={<Camera className="size-5" />}>
          Nueva foto
        </IosButton>
      </footer>
    </div>
  )
}

function NavBar({ title, onBack }: { title: string; onBack: () => void }) {
  return (
    <header className="flex min-h-11 items-center px-2">
      <button
        type="button"
        aria-label="Volver"
        onClick={onBack}
        className="flex min-h-11 w-24 items-center text-[17px] text-primary"
      >
        <ChevronLeft className="size-7 -ml-1" aria-hidden="true" />
        Atrás
      </button>
      <h2 className="flex-1 text-center text-[17px] font-semibold">{title}</h2>
      <span className="w-24" aria-hidden="true" />
    </header>
  )
}
