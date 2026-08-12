/**
 * Sidebar navigation
 */

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  FileText,
  AlertCircle,
  Activity,
  Settings,
} from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Transactions', href: '/transactions', icon: FileText },
  { name: 'Alerts', href: '/alerts', icon: AlertCircle },
  { name: 'Health', href: '/health', icon: Activity },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-slate-800 border-r border-slate-700 p-6 flex flex-col">
      <nav className="space-y-2 flex-1">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              )}
            >
              <Icon size={20} />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-slate-700 pt-6 mt-6">
        <p className="text-xs text-slate-500">Dashboard v0.1.0</p>
      </div>
    </aside>
  )
}
