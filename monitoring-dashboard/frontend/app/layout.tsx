/**
 * Main layout for the monitoring dashboard
 */

import type { Metadata } from 'next'
import './globals.css'
import Header from '@/components/Header'
import Sidebar from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'BankOps Monitoring Dashboard',
  description: 'Real-time transaction monitoring and operational visibility',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen bg-slate-900">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-auto bg-slate-900 p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
