/**
 * Alerts panel
 */

'use client'

import { useDashboardStore } from '@/store/dashboard'
import { AlertTriangle, Bell } from 'lucide-react'
import Link from 'next/link'

export default function AlertsPanel() {
  const { metrics } = useDashboardStore()

  const alerts = metrics?.active_alerts || []

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <p className="card-title">Active Alerts</p>
        <div className="flex items-center gap-2 text-red-400">
          <AlertTriangle size={16} />
          <span className="font-bold">{alerts.length}</span>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="text-slate-400 text-sm flex items-center gap-2">
          <Bell size={16} />
          No active alerts
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.slice(0, 5).map((alert: any) => (
            <div key={alert.id} className="text-sm p-2 bg-red-900 bg-opacity-20 rounded border border-red-800">
              <p className="text-red-200 font-medium">{alert.message}</p>
              <p className="text-red-300 text-xs mt-1">{alert.created_at}</p>
            </div>
          ))}
        </div>
      )}

      <Link href="/alerts" className="text-blue-400 text-sm mt-4 inline-block hover:text-blue-300">
        View all alerts →
      </Link>
    </div>
  )
}
