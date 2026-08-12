/**
 * Service health status
 */

'use client'

import { useDashboardStore } from '@/store/dashboard'
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react'

export default function ServiceHealth() {
  const { metrics } = useDashboardStore()

  const health = metrics?.health || {}

  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'HEALTHY':
        return <CheckCircle size={16} className="text-green-400" />
      case 'DEGRADED':
        return <AlertCircle size={16} className="text-yellow-400" />
      case 'DOWN':
        return <XCircle size={16} className="text-red-400" />
      default:
        return <AlertCircle size={16} className="text-slate-400" />
    }
  }

  return (
    <div className="card">
      <p className="card-title">Service Health</p>
      <div className="space-y-3">
        {Object.entries(health).map(([name, service]: [string, any]) => (
          <div key={name} className="flex items-center justify-between p-2 bg-slate-900 rounded">
            <span className="text-sm font-medium text-slate-200 capitalize">{name}</span>
            <div className="flex items-center gap-2">
              {getStatusIcon(service.status)}
              <span className="text-xs text-slate-400">{service.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
