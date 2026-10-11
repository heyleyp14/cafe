import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

// Inter is the fallback when the San Francisco system font is unavailable.
const _inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Detector de hojas de café · Maqueta',
  description:
    'Maqueta móvil (iPhone, estilo iOS) de una app para clasificar hojas de café. Prototipo académico sin backend.',
  generator: 'v0.app',
}

export const viewport: Viewport = {
  colorScheme: 'light',
  themeColor: '#f2f2f7',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className="bg-background">
      <body className="font-sans antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
