import Image from 'next/image'
import { cn } from '@/lib/utils'

/**
 * Generic phone outline drawn with CSS around a real screenshot of the app.
 * The screenshots are 1080x2400; the frame adds no fake interface on top.
 */
export function PhoneFrame({
  src,
  alt,
  eager = false,
  className,
}: {
  src: string
  alt: string
  eager?: boolean
  className?: string
}) {
  return (
    <div
      className={cn(
        'phone-frame w-60 shrink-0 rounded-[2.25rem] bg-phone p-2 sm:w-[17.5rem]',
        className,
      )}
    >
      {/* The inset matches the screenshots' own background so the status bar clears the corners. */}
      <div className="overflow-hidden rounded-[1.75rem] bg-[#f2f2f7] px-1.5 pt-2.5">
        <Image
          src={src}
          alt={alt}
          width={1080}
          height={2400}
          sizes="(min-width: 640px) 252px, 212px"
          loading={eager ? 'eager' : 'lazy'}
          fetchPriority={eager ? 'high' : 'auto'}
          className="h-auto w-full"
        />
      </div>
    </div>
  )
}
