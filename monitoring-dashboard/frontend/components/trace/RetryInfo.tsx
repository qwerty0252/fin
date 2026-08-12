/**
 * Retry information component
 */

'use client'

import { RotateCw } from 'lucide-react'

export default function RetryInfo({ trace }: any) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <RotateCw size={18} className="text-yellow-400" />
        <p className="card-title">Retry Information</p>
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-xs text-slate-400 uppercase">Retry Count</p>
          <p className="text-2xl font-bold text-slate-200 mt-1">{trace.retry_count}</p>
        </div>

        <div>
          <p className="text-xs text-slate-400 uppercase mb-2">Retry Events</p>
          <div className="space-y-2">
            {trace.timeline
              ?.filter((e: any) => e.event_type?.includes('RETRY'))
              .map((event: any) => (
                <div key={event.id} className="text-xs p-2 bg-slate-900 rounded border border-yellow-800">
                  <p className="text-yellow-200">{event.event_type}</p>
                  <p className="text-slate-400 mt-1">{event.timestamp}</p>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  )
}
