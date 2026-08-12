/**
 * Transaction details component
 */

'use client'

import { format } from 'date-fns'

export default function TransactionDetails({ trace }: any) {
  return (
    <div className="card space-y-4">
      <p className="card-title">Transaction Details</p>

      <div>
        <p className="text-xs text-slate-400 uppercase">Transaction ID</p>
        <p className="text-sm font-mono text-slate-200 mt-1">{trace.transaction_id}</p>
      </div>

      <div>
        <p className="text-xs text-slate-400 uppercase">Reference</p>
        <p className="text-sm font-mono text-slate-200 mt-1">{trace.reference}</p>
      </div>

      <div>
        <p className="text-xs text-slate-400 uppercase">Amount</p>
        <p className="metric-value text-2xl">{trace.amount}</p>
      </div>

      <div>
        <p className="text-xs text-slate-400 uppercase">Provider</p>
        <p className="text-sm text-slate-200 mt-1">{trace.provider}</p>
      </div>

      <div>
        <p className="text-xs text-slate-400 uppercase">Current State</p>
        <p className="text-sm px-3 py-1 bg-blue-900 text-blue-200 rounded mt-1 inline-block">
          {trace.current_state}
        </p>
      </div>

      <div>
        <p className="text-xs text-slate-400 uppercase">Total Processing Time</p>
        <p className="text-sm text-slate-200 mt-1">{trace.total_processing_time_ms}ms</p>
      </div>

      <div>
        <p className="text-xs text-slate-400 uppercase">Created</p>
        <p className="text-sm text-slate-200 mt-1">{format(new Date(trace.created_at), 'MMM dd, yyyy HH:mm:ss')}</p>
      </div>
    </div>
  )
}
