/**
 * Dashboard overview page
 */

'use client'

import { useEffect, useState } from 'react'
import MetricsGrid from '@/components/dashboard/MetricsGrid'
import TransactionStateChart from '@/components/dashboard/TransactionStateChart'
import RecentTransactions from '@/components/dashboard/RecentTransactions'
import AlertsPanel from '@/components/dashboard/AlertsPanel'
import ServiceHealth from '@/components/dashboard/ServiceHealth'
import { useDashboardStore } from '@/store/dashboard'
import { fetchDashboardMetrics } from '@/lib/api'

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const { setMetrics } = useDashboardStore()

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await fetchDashboardMetrics()
        setMetrics(data)
      } catch (error) {
        console.error('Failed to load metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    loadMetrics()

    // Refresh metrics every 5 seconds
    const interval = setInterval(loadMetrics, 5000)
    return () => clearInterval(interval)
  }, [setMetrics])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Dashboard</h1>
        <p className="text-slate-400 mt-1">Real-time transaction monitoring</p>
      </div>

      {/* Metrics Grid */}
      <MetricsGrid />

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          {/* Transaction State Distribution */}
          <TransactionStateChart />

          {/* Recent Transactions */}
          <RecentTransactions />
        </div>

        <div className="space-y-6">
          {/* Alerts */}
          <AlertsPanel />

          {/* Service Health */}
          <ServiceHealth />
        </div>
      </div>
    </div>
  )
}
