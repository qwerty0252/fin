/**
 * Queue metrics component
 */

'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function QueueMetrics({ health }: any) {
  const queueData = [
    { name: 'Incoming', value: 245 },
    { name: 'Processing', value: 89 },
    { name: 'Retry', value: 34 },
    { name: 'Dead Letter', value: 2 },
  ]

  return (
    <div className="card">
      <p className="card-title">Queue Metrics</p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={queueData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="name" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" />
          <Tooltip />
          <Bar dataKey="value" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
