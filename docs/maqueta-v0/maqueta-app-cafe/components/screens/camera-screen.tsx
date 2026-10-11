import Image from 'next/image'
import { Zap, CameraOff } from 'lucide-react'
import { SAMPLE_PHOTO } from '@/lib/mock-data'

type CameraScreenProps = {
  onBack: () => void
  onCapture: () => void
}

export function CameraScreen({ onBack, onCapture }: CameraScreenProps) {
  return (
    <div className="relative flex flex-1 flex-col bg-scrim text-scrim-foreground">
      <Image
        src={SAMPLE_PHOTO}
        alt="Vista previa de la cámara con una hoja de café"
        fill
        sizes="390px"
        priority
        className="object-cover opacity-90"
      />

      <header className="relative z-10 flex items-center justify-between px-4 pt-3">
        <button
          type="button"
          onClick={onBack}
          className="min-h-11 text-[17px] text-scrim-foreground drop-shadow"
        >
          Cancelar
        </button>
        <button
          type="button"
          aria-label="Flash desactivado"
          className="flex size-11 items-center justify-center rounded-full bg-scrim/40 backdrop-blur-md"
        >
          <Zap className="size-5" />
        </button>
      </header>

      <div className="relative z-10 flex flex-1 flex-col items-center justify-center px-8">
        <div aria-hidden="true" className="relative aspect-[3/4] w-full max-w-[280px]">
          <Corner className="left-0 top-0 rounded-tl-lg border-l-[3px] border-t-[3px]" />
          <Corner className="right-0 top-0 rounded-tr-lg border-r-[3px] border-t-[3px]" />
          <Corner className="bottom-0 left-0 rounded-bl-lg border-b-[3px] border-l-[3px]" />
          <Corner className="bottom-0 right-0 rounded-br-lg border-b-[3px] border-r-[3px]" />
        </div>
        <p className="mt-6 rounded-full bg-scrim/40 px-4 py-2 text-[13px] font-medium backdrop-blur-md">
          Encuadra una sola hoja dentro del marco
        </p>
      </div>

      <footer className="relative z-10 flex h-44 flex-col items-center justify-center gap-5 bg-scrim/70 backdrop-blur-xl">
        <span className="text-[13px] font-semibold uppercase tracking-wider text-accent">
          Foto
        </span>
        <button
          type="button"
          onClick={onCapture}
          aria-label="Capturar foto"
          className="flex size-[72px] items-center justify-center rounded-full border-[3px] border-scrim-foreground focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-scrim-foreground"
        >
          <span
            aria-hidden="true"
            className="size-[60px] rounded-full bg-scrim-foreground transition-transform active:scale-90"
          />
        </button>
      </footer>
    </div>
  )
}

export function CameraDeniedScreen({
  onBack,
  onOpenSettings,
}: {
  onBack: () => void
  onOpenSettings: () => void
}) {
  return (
    <div className="relative flex flex-1 flex-col bg-scrim">
      <Image
        src={SAMPLE_PHOTO}
        alt=""
        fill
        sizes="390px"
        className="object-cover opacity-30 blur-sm"
      />
      <div className="absolute inset-0 bg-scrim/40" />

      <div className="relative z-10 flex flex-1 items-center justify-center px-10">
        <section
          role="alertdialog"
          aria-labelledby="permiso-titulo"
          aria-describedby="permiso-desc"
          className="w-full max-w-[270px] overflow-hidden rounded-[14px] bg-background/95 text-center backdrop-blur-xl"
        >
          <div className="flex flex-col items-center gap-2 px-4 pt-5 pb-4">
            <CameraOff className="size-8 text-muted-foreground" aria-hidden="true" />
            <h1 id="permiso-titulo" className="text-[17px] font-semibold text-balance">
              Sin acceso a la cámara
            </h1>
            <p id="permiso-desc" className="text-[13px] leading-relaxed text-foreground text-pretty">
              Para fotografiar la hoja, permite el acceso a la cámara en Ajustes.
            </p>
          </div>
          <div className="flex flex-col border-t border-separator">
            <button
              type="button"
              onClick={onOpenSettings}
              className="min-h-11 border-b border-separator text-[17px] font-semibold text-primary active:bg-surface-high"
            >
              Abrir Ajustes
            </button>
            <button
              type="button"
              onClick={onBack}
              className="min-h-11 text-[17px] text-primary active:bg-surface-high"
            >
              Volver al inicio
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}

function Corner({ className }: { className: string }) {
  return (
    <span className={`absolute size-8 border-scrim-foreground drop-shadow ${className}`} />
  )
}
