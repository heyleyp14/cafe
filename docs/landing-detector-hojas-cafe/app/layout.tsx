import type { Metadata, Viewport } from 'next'
import { Roboto } from 'next/font/google'
import './globals.css'

// Roboto is the typeface the Android app itself renders with.
const roboto = Roboto({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-roboto',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Detector de hojas de café',
  description:
    'Clasifica una foto de una hoja de café en sana, roya o minador. Funciona en el teléfono, sin internet. Prototipo académico de apoyo para Android.',
  icons: {
    icon: [{ url: '/icono-app.svg', type: 'image/svg+xml' }],
    shortcut: '/icono-app.svg',
    apple: '/icono-app.svg',
  },
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
    <html lang="es" className={`${roboto.variable} bg-background`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
