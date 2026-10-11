'use client'

import { useState } from 'react'
import type { Screen } from '@/lib/mock-data'
import { PhoneFrame } from '@/components/phone-frame'
import { HomeScreen } from '@/components/screens/home-screen'
import {
  CameraScreen,
  CameraDeniedScreen,
} from '@/components/screens/camera-screen'
import {
  ResultAcceptedScreen,
  ResultLowConfidenceScreen,
} from '@/components/screens/result-screen'
import { cn } from '@/lib/utils'

const SCREEN_LABELS: Record<Screen, string> = {
  home: 'Inicio',
  camera: 'Cámara',
  'camera-denied': 'Cámara · permiso denegado',
  'result-ok': 'Resultado aceptado',
  'result-low': 'Resultado · confianza baja',
}

export function MockupApp() {
  const [screen, setScreen] = useState<Screen>('home')
  const [permissionDenied, setPermissionDenied] = useState(false)

  const goHome = () => setScreen('home')
  const openCamera = () =>
    setScreen(permissionDenied ? 'camera-denied' : 'camera')

  const current = (() => {
    switch (screen) {
      case 'home':
        return (
          <HomeScreen
            onTakePhoto={openCamera}
            onPickGallery={() => setScreen('result-low')}
          />
        )
      case 'camera':
        return (
          <CameraScreen onBack={goHome} onCapture={() => setScreen('result-ok')} />
        )
      case 'camera-denied':
        return (
          <CameraDeniedScreen
            onBack={goHome}
            onOpenSettings={() => {
              setPermissionDenied(false)
              setScreen('camera')
            }}
          />
        )
      case 'result-ok':
        return <ResultAcceptedScreen onBack={goHome} onNewPhoto={openCamera} />
      case 'result-low':
        return (
          <ResultLowConfidenceScreen onBack={goHome} onNewPhoto={openCamera} />
        )
    }
  })()

  return (
    <div className="flex flex-col items-center gap-8 lg:flex-row lg:items-start lg:gap-12">
      <PhoneFrame dark={screen === 'camera'}>{current}</PhoneFrame>

      <aside className="w-full max-w-[360px] lg:pt-6" aria-label="Controles de la maqueta">
        <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
          Pantallas
        </h2>
        <nav className="mt-3 flex flex-col gap-2">
          {(Object.keys(SCREEN_LABELS) as Screen[]).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => setScreen(key)}
              aria-current={screen === key ? 'page' : undefined}
              className={cn(
                'flex min-h-12 items-center rounded-full px-5 text-left text-base transition-colors',
                screen === key
                  ? 'bg-primary-container font-medium text-primary-container-foreground'
                  : 'bg-surface-low text-foreground hover:bg-surface-high',
              )}
            >
              {SCREEN_LABELS[key]}
            </button>
          ))}
        </nav>

        <label className="mt-6 flex min-h-12 cursor-pointer items-center justify-between gap-4 rounded-2xl bg-surface-low px-5 py-3">
          <span className="text-base">Simular permiso denegado</span>
          <input
            type="checkbox"
            checked={permissionDenied}
            onChange={(e) => setPermissionDenied(e.target.checked)}
            className="size-5 accent-primary"
          />
        </label>

        <dl className="mt-6 flex flex-col gap-2 text-sm leading-relaxed text-muted-foreground">
          <div>
            <dt className="font-medium text-foreground">Flujo de ejemplo</dt>
            <dd>
              «Tomar foto» abre la cámara; capturar muestra el resultado
              aceptado. «Elegir de la fototeca» muestra la variante de confianza baja.
            </dd>
          </div>
          <div>
            <dt className="font-medium text-foreground">Datos</dt>
            <dd>Fijos y de ejemplo. Sin backend, cuentas ni historial.</dd>
          </div>
        </dl>
      </aside>
    </div>
  )
}
