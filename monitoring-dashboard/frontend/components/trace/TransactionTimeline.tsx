/**
 * Transaction timeline component
 */

'use client'

import { format } from 'date-fns'
import { CheckCircle, AlertCircle } from 'lucide-react'

export default function TransactionTimeline({ trace }: any) {
  if (!trace || !trace.timeline) {
    return <div className="card text-slate-400">No events found</div>
  }

  return (
    <div className="card">
      <p className="card-title">Transaction Timeline</p>
      <div className="space-y-4 mt-6">
        {trace.timeline.map((event: any, index: number) => (
          <div key={event.id} className="flex gap-4">
            {/* Timeline line and dot */}
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-blue-600 border-2 border-blue-400 flex items-center justify-center">
                <CheckCircle size={16} className="text-white" />
              </div>
              {index < trace.timeline.length - 1 && (
                <div className="w-1 h-16 bg-blue-600 my-2"></div>
              )}
            </div>

            {/* Event details */}
            <div className="flex-1 pb-4">
              <div className="bg-slate-900 rounded-lg p-4">
                <p className="font-medium text-slate-200">{event.event_type}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {format(new Date(event.timestamp), 'MMM dd, HH:mm:ss')}
                </p>
                {event.processing_time_ms && (
                  <p className="text-xs text-slate-500 mt-2">
                    Processing time: {event.processing_time_ms}ms
                  </p>
                )}
                {event.payload && (
                  <details className="mt-2">
                    <summary className="text-xs text-blue-400 cursor-pointer">View details</summary>
                    <pre className="text-xs bg-slate-800 p-2 mt-2 rounded overflow-auto max-h-48">
                      {JSON.stringify(event.payload, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
