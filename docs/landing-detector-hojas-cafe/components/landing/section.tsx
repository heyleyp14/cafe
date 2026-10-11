import { cn } from '@/lib/utils'

export function Section({
  id,
  title,
  className,
  children,
}: {
  id: string
  title: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <section id={id} aria-labelledby={`${id}-title`} className={cn('flex flex-col gap-5', className)}>
      <h2
        id={`${id}-title`}
        className="text-[1.75rem] leading-tight font-bold tracking-[-0.02em] text-balance sm:text-[2rem]"
      >
        {title}
      </h2>
      {children}
    </section>
  )
}

/** White inset group on the grey page, as in the app's own lists. */
export function Group({
  as: Tag = 'ul',
  className,
  children,
}: {
  as?: 'ul' | 'ol' | 'div'
  className?: string
  children: React.ReactNode
}) {
  return (
    <Tag className={cn('overflow-hidden rounded-[20px] bg-card text-card-foreground', className)}>
      {children}
    </Tag>
  )
}

/** A row with a leading element; the hairline starts where the text starts. */
export function GroupRow({
  leading,
  first = false,
  children,
}: {
  leading: React.ReactNode
  first?: boolean
  children: React.ReactNode
}) {
  return (
    <li className="flex items-start gap-4 pl-4">
      <span className="flex h-[3.75rem] shrink-0 items-center">{leading}</span>
      <div
        className={cn(
          'flex min-h-[3.75rem] flex-1 items-center py-4 pr-4',
          !first && 'border-t border-separator',
        )}
      >
        <p className="leading-normal text-pretty">{children}</p>
      </div>
    </li>
  )
}
