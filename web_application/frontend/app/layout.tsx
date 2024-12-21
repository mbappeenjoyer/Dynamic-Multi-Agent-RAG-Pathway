import './globals.css'
import type { Metadata } from 'next'
import { Inter, Outfit, Plus_Jakarta_Sans } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] });
const outfit = Outfit({ subsets: ['latin'] });
const jakarta = Plus_Jakarta_Sans({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AgentRAG',
  description: 'AgentRAG',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}

