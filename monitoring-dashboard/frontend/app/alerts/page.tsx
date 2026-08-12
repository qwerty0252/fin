/**
 * Alerts page
 */

'use client'

import { useState, useEffect } from 'react'
import AlertsList from '@/components/alerts/AlertsList'
import AlertsSummary from '@/components/alerts/AlertsSummary'
import { fetchAlerts } from '@/lib/api'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        setLoading(true)
        const data = await fetchAlerts()
        setAlerts(data)
      } catch (error) {
        console.error('Failed to load alerts:', error)
      } finally {
        setLoading(false)
      }
    }

    loadAlerts()

    // Refresh alerts every 10 seconds
    const interval = setInterval(loadAlerts, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Alerts</h1>
        <p className="text-slate-400 mt-1">Monitor system alerts and incidents</p>
      </div>

      <AlertsSummary alerts={alerts} />
      <AlertsList alerts={alerts} loading={loading} />
    </div>
  )
}
