import { cn } from '@/lib/utils'

type IosButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'filled' | 'tinted' | 'plain'
  icon?: React.ReactNode
}

const variants: Record<NonNullable<IosButtonProps['variant']>, string> = {
  filled: 'bg-primary text-primary-foreground',
  tinted: 'bg-primary-container text-secondary-foreground',
  plain: 'bg-transparent text-primary',
}

export function IosButton({
  variant = 'filled',
  icon,
  className,
  children,
  ...props
}: IosButtonProps) {
  return (
    <button
      type="button"
      className={cn(
        'flex h-[50px] w-full items-center justify-center gap-2 rounded-xl px-5 text-[17px] font-semibold tracking-tight transition-[opacity,transform] active:scale-[0.98] active:opacity-70 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring',
        variants[variant],
        className,
      )}
      {...props}
    >
      {icon && <span aria-hidden="true">{icon}</span>}
      {children}
    </button>
  )
}
