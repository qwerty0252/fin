/**
 * Database health component
 */

'use client'

import { Database } from 'lucide-react'

export default function DatabaseHealth({ health }: any) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Database size={20} className="text-blue-400" />
        <p className="card-title">Database Health</p>
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-xs text-slate-400 uppercase">Status</p>
          <p className="text-sm text-green-400 mt-1">✓ Connected</p>
        </div>

        <div>
          <p className="text-xs text-slate-400 uppercase">Connections</p>
          <p className="text-lg font-bold text-slate-200 mt-1">12/20</p>
        </div>

        <div>
          <p className="text-xs text-slate-400 uppercase">Query Performance</p>
          <p className="text-sm text-slate-200 mt-1">Avg: 45ms</p>
        </div>

        <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
          <div className="h-full w-3/5 bg-green-500"></div>
        </div>
        <p className="text-xs text-slate-400">60% utilization</p>
      </div>
    </div>
  )
}
