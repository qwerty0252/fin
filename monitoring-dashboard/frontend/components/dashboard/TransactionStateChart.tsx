/**
 * Transaction state distribution chart
 */

'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useDashboardStore } from '@/store/dashboard'

export default function TransactionStateChart() {
  const { metrics } = useDashboardStore()

  if (!metrics?.transactions_by_state) {
    return <div className="card text-slate-400">Loading state data...</div>
  }

  const data = Object.entries(metrics.transactions_by_state).map(([state, count]) => ({
    name: state,
    count: count,
  }))

  return (
    <div className="card">
      <p className="card-title">Transaction State Distribution</p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="name" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" />
          <Tooltip />
          <Bar dataKey="count" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
