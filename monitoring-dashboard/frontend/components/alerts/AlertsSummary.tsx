/**
 * Alerts summary component
 */

'use client'

import { AlertTriangle } from 'lucide-react'

export default function AlertsSummary({ alerts }: any) {
  const critical = alerts?.filter((a: any) => a.severity === 'CRITICAL').length || 0
  const warning = alerts?.filter((a: any) => a.severity === 'WARNING').length || 0
  const info = alerts?.filter((a: any) => a.severity === 'INFO').length || 0

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="card border-l-4 border-red-500">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase">Critical</p>
            <p className="text-2xl font-bold text-red-400 mt-1">{critical}</p>
          </div>
          <AlertTriangle size={32} className="text-red-400 opacity-30" />
        </div>
      </div>

      <div className="card border-l-4 border-yellow-500">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase">Warning</p>
            <p className="text-2xl font-bold text-yellow-400 mt-1">{warning}</p>
          </div>
          <AlertTriangle size={32} className="text-yellow-400 opacity-30" />
        </div>
      </div>

      <div className="card border-l-4 border-blue-500">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase">Info</p>
            <p className="text-2xl font-bold text-blue-400 mt-1">{info}</p>
          </div>
          <AlertTriangle size={32} className="text-blue-400 opacity-30" />
        </div>
      </div>
    </div>
  )
}
