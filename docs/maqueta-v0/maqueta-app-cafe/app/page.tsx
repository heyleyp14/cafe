import { MockupApp } from '@/components/mockup-app'

export default function Page() {
  return (
    <main className="min-h-svh bg-surface-high px-4 py-8 lg:py-12">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-8">
        <header className="flex flex-col gap-1">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Maqueta · iPhone 390×844
          </p>
          <h1 className="text-2xl font-medium text-balance">
            Detector de hojas de café
          </h1>
        </header>
        <MockupApp />
      </div>
    </main>
  )
}
