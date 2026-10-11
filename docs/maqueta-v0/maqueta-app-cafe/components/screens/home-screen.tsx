'use client'

import { useState } from 'react'
import { Camera, Images, Leaf, Sun, Focus, Square, ChevronRight } from 'lucide-react'
import { ABOUT } from '@/lib/mock-data'
import { IosButton } from '@/components/ios-button'

type HomeScreenProps = {
  onTakePhoto: () => void
  onPickGallery: () => void
}

const TIPS = [
  { icon: Leaf, text: 'Una sola hoja' },
  { icon: Sun, text: 'Buena luz natural' },
  { icon: Focus, text: 'Imagen enfocada' },
  { icon: Square, text: 'Fondo simple' },
]

export function HomeScreen({ onTakePhoto, onPickGallery }: HomeScreenProps) {
  const [aboutOpen, setAboutOpen] = useState(false)

  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <header className="px-4 pt-3 pb-2">
        <h1 className="text-[34px] font-bold leading-tight tracking-tight text-balance">
          Hojas de café
        </h1>
        <p className="mt-1 text-[15px] text-muted-foreground">
          Clasificador de enfermedades
        </p>
      </header>

      <main className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-4 pt-2">
        <section aria-labelledby="instrucciones" className="flex flex-col gap-2">
          <h2
            id="instrucciones"
            className="px-4 text-[13px] uppercase tracking-wide text-muted-foreground"
          >
            Cómo tomar la foto
          </h2>
          <ul className="overflow-hidden rounded-xl bg-surface-low">
            {TIPS.map(({ icon: Icon, text }, i) => (
              <li
                key={text}
                className="flex items-center gap-3 pl-4"
              >
                <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
                  <Icon className="size-4" aria-hidden="true" />
                </span>
                <span
                  className={`flex min-h-11 flex-1 items-center pr-4 text-[17px] ${
                    i < TIPS.length - 1 ? 'border-b border-separator' : ''
                  }`}
                >
                  {text}
                </span>
              </li>
            ))}
          </ul>
        </section>

        <div className="flex flex-col gap-3">
          <IosButton onClick={onTakePhoto} icon={<Camera className="size-5" />}>
            Tomar foto
          </IosButton>
          <IosButton
            variant="tinted"
            onClick={onPickGallery}
            icon={<Images className="size-5" />}
          >
            Elegir de la fototeca
          </IosButton>
        </div>

        <section className="mt-auto flex flex-col gap-2 pb-4">
          <button
            type="button"
            onClick={() => setAboutOpen(true)}
            className="flex min-h-11 w-full items-center justify-between rounded-xl bg-surface-low px-4 text-[17px] active:bg-surface-high"
          >
            <span>Acerca de</span>
            <ChevronRight className="size-5 text-outline" aria-hidden="true" />
          </button>
          <p role="note" className="px-4 text-[13px] leading-relaxed text-muted-foreground">
            Prototipo académico de apoyo. No es una herramienta de diagnóstico.
          </p>
        </section>
      </main>

      {aboutOpen && <AboutSheet onClose={() => setAboutOpen(false)} />}
    </div>
  )
}

function AboutSheet({ onClose }: { onClose: () => void }) {
  return (
    <div className="absolute inset-0 z-10 flex flex-col justify-end">
      <button
        type="button"
        aria-label="Cerrar"
        onClick={onClose}
        className="absolute inset-0 bg-scrim/40"
      />
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="acerca-titulo"
        className="relative flex max-h-[80%] flex-col rounded-t-[1.25rem] bg-background animate-in slide-in-from-bottom duration-300"
      >
        <div aria-hidden="true" className="mx-auto mt-2 h-[5px] w-9 rounded-full bg-outline/60" />
        <header className="flex items-center justify-between px-4 pt-3 pb-2">
          <span className="w-16" />
          <h2 id="acerca-titulo" className="text-[17px] font-semibold">
            Acerca de
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="w-16 text-right text-[17px] font-semibold text-primary"
          >
            OK
          </button>
        </header>

        <div className="flex flex-col gap-6 overflow-y-auto px-4 pb-10 pt-2">
          <section className="flex flex-col gap-2">
            <h3 className="px-4 text-[13px] uppercase tracking-wide text-muted-foreground">
              Modelo
            </h3>
            <div className="flex min-h-11 items-center justify-between rounded-xl bg-surface-low px-4 text-[17px]">
              <span>Versión</span>
              <span className="text-muted-foreground">{ABOUT.modelVersion}</span>
            </div>
          </section>

          <section className="flex flex-col gap-2">
            <h3 className="px-4 text-[13px] uppercase tracking-wide text-muted-foreground">
              Créditos de los datasets
            </h3>
            <ul className="overflow-hidden rounded-xl bg-surface-low pl-4">
              {ABOUT.datasets.map((d, i) => (
                <li
                  key={d.name}
                  className={`py-2.5 pr-4 ${
                    i < ABOUT.datasets.length - 1 ? 'border-b border-separator' : ''
                  }`}
                >
                  <p className="text-[17px]">{d.name}</p>
                  <p className="text-[15px] text-muted-foreground">{d.detail}</p>
                </li>
              ))}
            </ul>
            <p className="px-4 text-[13px] leading-relaxed text-muted-foreground">
              Prototipo académico de apoyo. No es una herramienta de diagnóstico.
            </p>
          </section>
        </div>
      </section>
    </div>
  )
}
