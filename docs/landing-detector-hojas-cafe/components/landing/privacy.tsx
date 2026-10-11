import { WifiOff, Camera } from 'lucide-react'
import { Group, GroupRow, Section } from './section'

const tile =
  'flex size-9 items-center justify-center rounded-[10px] bg-secondary text-secondary-foreground'

export function Privacy() {
  return (
    <Section id="privacidad" title="Privacidad">
      <Group>
        <GroupRow
          first
          leading={
            <span className={tile}>
              <WifiOff className="size-5" aria-hidden="true" />
            </span>
          }
        >
          La app no tiene permiso de internet. Las fotos no salen del teléfono.
        </GroupRow>
        <GroupRow
          leading={
            <span className={tile}>
              <Camera className="size-5" aria-hidden="true" />
            </span>
          }
        >
          Permiso que solicita: cámara.
        </GroupRow>
      </Group>
    </Section>
  )
}
