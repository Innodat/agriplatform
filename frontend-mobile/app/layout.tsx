

import './globals.css'
import { Toaster } from "@/components/ui/toaster"

export const metadata = {
  title: 'Receipts',
  description: 'Capture Your Receipts',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" href="/favicon.png" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet" />
        <style>{`
html {
  font-family: 'Inter', sans-serif;
}
        `}</style>
      </head>
      <body>
        {children}
        {/* Toast notifications */}
        <Toaster />
      </body>
    </html>
  )
}
