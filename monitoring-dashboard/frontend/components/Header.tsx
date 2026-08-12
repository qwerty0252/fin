/**
 * Header component
 */

'use client'

import { Clock } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Header() {
  const [time, setTime] = useState<string>('')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString())
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">BankOps</h1>
        <p className="text-sm text-slate-400">Monitoring Dashboard</p>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-slate-300">
          <Clock size={18} />
          <span className="font-mono text-sm">{time}</span>
        </div>
      </div>
    </header>
  )
}
