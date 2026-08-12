/**
 * Service status component
 */

'use client'

import { CheckCircle, AlertCircle, XCircle } from 'lucide-react'

export default function ServiceStatus({ health }: any) {
  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'HEALTHY':
        return <CheckCircle size={20} className="text-green-400" />
      case 'DEGRADED':
        return <AlertCircle size={20} className="text-yellow-400" />
      case 'DOWN':
        return <XCircle size={20} className="text-red-400" />
      default:
        return <AlertCircle size={20} className="text-slate-400" />
    }
  }

  const services = [
    { name: 'API Server', status: 'HEALTHY' },
    { name: 'Database', status: 'HEALTHY' },
    { name: 'RabbitMQ', status: 'HEALTHY' },
    { name: 'Redis', status: 'HEALTHY' },
  ]

  return (
    <div className="card">
      <p className="card-title">Service Status</p>
      <div className="space-y-3 mt-4">
        {services.map((service) => (
          <div key={service.name} className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
            <div className="flex items-center gap-3">
              {getStatusIcon(service.status)}
              <span className="text-sm font-medium text-slate-200">{service.name}</span>
            </div>
            <span className="text-xs px-2 py-1 bg-green-900 text-green-200 rounded">
              {service.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
