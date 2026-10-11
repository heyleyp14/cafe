import { Signal, Wifi, BatteryFull } from 'lucide-react'
import { cn } from '@/lib/utils'

type PhoneFrameProps = {
  children: React.ReactNode
  dark?: boolean
}

export function PhoneFrame({ children, dark = false }: PhoneFrameProps) {
  return (
    <div
      className="relative w-[390px] h-[844px] shrink-0 rounded-[3.4rem] bg-scrim p-[12px] shadow-2xl ring-1 ring-foreground/20"
      role="region"
      aria-label="Pantalla de teléfono iPhone, 390 por 844"
    >
      {/* Side buttons */}
      <span aria-hidden="true" className="absolute -left-[3px] top-[120px] h-8 w-[3px] rounded-l bg-scrim" />
      <span aria-hidden="true" className="absolute -left-[3px] top-[180px] h-16 w-[3px] rounded-l bg-scrim" />
      <span aria-hidden="true" className="absolute -left-[3px] top-[260px] h-16 w-[3px] rounded-l bg-scrim" />
      <span aria-hidden="true" className="absolute -right-[3px] top-[200px] h-24 w-[3px] rounded-r bg-scrim" />

      <div
        className={cn(
          'relative flex h-full w-full flex-col overflow-hidden rounded-[2.75rem]',
          dark ? 'bg-scrim text-scrim-foreground' : 'bg-background text-foreground',
        )}
      >
        <StatusBar dark={dark} />
        <div className="relative flex-1 min-h-0 flex flex-col">{children}</div>
        <div
          aria-hidden="true"
          className={cn(
            'h-6 flex items-end justify-center pb-2',
            dark ? 'bg-transparent' : 'bg-background',
          )}
        >
          <div
            className={cn(
              'h-[5px] w-[134px] rounded-full',
              dark ? 'bg-scrim-foreground/80' : 'bg-foreground/80',
            )}
          />
        </div>
      </div>
    </div>
  )
}

function StatusBar({ dark }: { dark: boolean }) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        'relative h-12 flex items-center justify-between px-8 pt-2 text-[15px] font-semibold',
        dark ? 'text-scrim-foreground' : 'text-foreground',
      )}
    >
      <span>9:41</span>
      {/* Dynamic Island */}
      <span className="absolute left-1/2 top-3 h-[34px] w-[122px] -translate-x-1/2 rounded-full bg-scrim" />
      <span className="flex items-center gap-1.5">
        <Signal className="size-4" />
        <Wifi className="size-4" />
        <BatteryFull className="size-5" />
      </span>
    </div>
  )
}
