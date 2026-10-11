import { Download } from 'lucide-react'
import { Notice } from './notice'
import { PhoneFrame } from './phone-frame'

export function Hero() {
  return (
    <section
      aria-labelledby="titulo"
      className="grid items-center gap-12 lg:grid-cols-[minmax(0,1fr)_auto] lg:gap-20"
    >
      <div className="flex flex-col items-start gap-6">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/icono-app.svg"
          alt="Logotipo de BioCafe"
          width={72}
          height={72}
          className="size-16 sm:size-[4.5rem]"
        />
        <div className="flex flex-col gap-3">
          <h1
            id="titulo"
            className="text-[2.5rem] leading-[1.05] font-bold tracking-[-0.025em] text-balance sm:text-6xl"
          >
            BioCafe
          </h1>
          <p className="max-w-[34rem] text-lg leading-relaxed text-pretty text-muted-foreground sm:text-xl">
            Clasifica una foto de una hoja de café en sana, roya o minador. Funciona en el teléfono,
            sin internet.
          </p>
        </div>
        <div className="flex w-full flex-col items-start gap-3">
          <a
            href="/DetectorHojasCafe-v2.0.apk"
            download
            className="inline-flex h-14 w-full items-center justify-center gap-3 rounded-full bg-primary px-9 text-lg font-medium whitespace-nowrap text-primary-foreground transition-[background-color,transform] duration-200 ease-out hover:bg-primary-hover active:scale-[0.98] sm:w-auto"
          >
            <Download className="size-5" aria-hidden="true" />
            Descargar APK
          </a>
          <p className="text-sm text-muted-foreground tabular-nums">
            Versión 2.0 · 47 MB · Android 8.0 o superior
          </p>
        </div>
        <Notice />
      </div>
      <PhoneFrame
        src="/app-inicio.png"
        alt="Captura de la pantalla de inicio de la app, con los consejos para tomar la foto y los botones Tomar foto y Elegir de galería."
        eager
        className="phone-enter mx-auto"
      />
    </section>
  )
}
