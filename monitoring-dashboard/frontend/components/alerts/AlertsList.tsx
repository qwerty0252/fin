/**
 * Alerts list component
 */

'use client'

import { format } from 'date-fns'
import { AlertTriangle, AlertCircle, Info } from 'lucide-react'

interface AlertsListProps {
  alerts: any[]
  loading: boolean
}

export default function AlertsList({ alerts, loading }: AlertsListProps) {
  if (loading) {
    return <div className="card text-slate-400">Loading alerts...</div>
  }

  if (!alerts || alerts.length === 0) {
    return <div className="card text-slate-400">No alerts at this time</div>
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return <AlertTriangle size={18} className="text-red-400" />
      case 'WARNING':
        return <AlertCircle size={18} className="text-yellow-400" />
      case 'INFO':
        return <Info size={18} className="text-blue-400" />
      default:
        return <AlertCircle size={18} className="text-slate-400" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'border-l-4 border-red-500 bg-red-900 bg-opacity-20'
      case 'WARNING':
        return 'border-l-4 border-yellow-500 bg-yellow-900 bg-opacity-20'
      case 'INFO':
        return 'border-l-4 border-blue-500 bg-blue-900 bg-opacity-20'
      default:
        return 'border-l-4 border-slate-500 bg-slate-800'
    }
  }

  return (
    <div className="card">
      <p className="card-title">Alert History</p>
      <div className="space-y-3 mt-4">
        {alerts.map((alert) => (
          <div key={alert.id} className={`p-4 rounded-lg ${getSeverityColor(alert.severity)}`}>
            <div className="flex items-start gap-3">
              {getSeverityIcon(alert.severity)}
              <div className="flex-1">
                <p className="font-medium text-slate-200">{alert.message}</p>
                <p className="text-xs text-slate-400 mt-1">
                  Type: {alert.alert_type}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  {format(new Date(alert.created_at), 'MMM dd, HH:mm:ss')}
                </p>
                {alert.resolved_at && (
                  <p className="text-xs text-green-400 mt-1">
                    Resolved: {format(new Date(alert.resolved_at), 'MMM dd, HH:mm:ss')}
                  </p>
                )}
              </div>
              <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                {alert.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
