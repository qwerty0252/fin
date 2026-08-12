/**
 * Metrics grid component showing key metrics
 */

'use client'

import { useDashboardStore } from '@/store/dashboard'
import { ArrowUp, ArrowDown } from 'lucide-react'

export default function MetricsGrid() {
  const { metrics } = useDashboardStore()

  if (!metrics) {
    return <div className="text-slate-400">Loading metrics...</div>
  }

  const metricItems = [
    {
      label: 'TPS',
      value: metrics.metrics?.tps?.toFixed(2) || '0',
      unit: 'tx/s',
      change: '+5%',
    },
    {
      label: 'Success Rate',
      value: metrics.metrics?.success_rate?.toFixed(1) || '0',
      unit: '%',
      change: '+2%',
    },
    {
      label: 'Avg Latency',
      value: metrics.metrics?.avg_latency_ms?.toFixed(0) || '0',
      unit: 'ms',
      change: '-10%',
    },
    {
      label: 'Active Transactions',
      value: metrics.metrics?.active_transactions || '0',
      unit: 'txs',
      change: '+15',
    },
  ]

  return (
    <div className="grid grid-cols-4 gap-4">
      {metricItems.map((item) => (
        <div key={item.label} className="card">
          <p className="card-title text-sm">{item.label}</p>
          <div className="metric-value">
            {item.value}
            <span className="text-sm text-slate-400 ml-2">{item.unit}</span>
          </div>
          <div className="flex items-center gap-1 mt-2 text-sm text-green-400">
            <ArrowUp size={14} />
            {item.change}
          </div>
        </div>
      ))}
    </div>
  )
}
