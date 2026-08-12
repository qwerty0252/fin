/**
 * System health page
 */

'use client'

import { useState, useEffect } from 'react'
import ServiceStatus from '@/components/health/ServiceStatus'
import DatabaseHealth from '@/components/health/DatabaseHealth'
import QueueMetrics from '@/components/health/QueueMetrics'
import { fetchHealthStatus } from '@/lib/api'

export default function HealthPage() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadHealth = async () => {
      try {
        setLoading(true)
        const data = await fetchHealthStatus()
        setHealth(data)
      } catch (error) {
        console.error('Failed to load health status:', error)
      } finally {
        setLoading(false)
      }
    }

    loadHealth()

    // Refresh every 10 seconds
    const interval = setInterval(loadHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400">Loading health status...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">System Health</h1>
        <p className="text-slate-400 mt-1">Monitor service status and infrastructure</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <ServiceStatus health={health} />
        <DatabaseHealth health={health} />
      </div>

      <QueueMetrics health={health} />
    </div>
  )
}
