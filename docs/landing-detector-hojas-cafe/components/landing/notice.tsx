import { TriangleAlert } from 'lucide-react'

export function Notice() {
  return (
    <div
      role="note"
      className="flex w-fit max-w-full items-start gap-3 rounded-[20px] bg-warning px-4 py-3.5 text-warning-foreground"
    >
      <TriangleAlert className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
      <p className="font-medium leading-snug text-pretty">
        Prototipo académico de apoyo. No es una herramienta de diagnóstico.
      </p>
    </div>
  )
}
