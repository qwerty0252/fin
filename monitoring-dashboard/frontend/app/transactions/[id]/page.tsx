/**
 * Transaction trace/details page
 */

'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import TransactionTimeline from '@/components/trace/TransactionTimeline'
import TransactionDetails from '@/components/trace/TransactionDetails'
import RetryInfo from '@/components/trace/RetryInfo'
import { fetchTransactionTrace } from '@/lib/api'

export default function TransactionTracePage() {
  const params = useParams()
  const transactionId = params.id as string
  const [trace, setTrace] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadTrace = async () => {
      try {
        setLoading(true)
        const data = await fetchTransactionTrace(transactionId)
        setTrace(data)
      } catch (error) {
        console.error('Failed to load transaction trace:', error)
      } finally {
        setLoading(false)
      }
    }

    loadTrace()
  }, [transactionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400">Loading transaction trace...</div>
      </div>
    )
  }

  if (!trace) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400">Transaction not found</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Transaction Trace</h1>
        <p className="text-slate-400 mt-1">{trace.transaction_id}</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          {/* Timeline */}
          <TransactionTimeline trace={trace} />
        </div>

        <div className="space-y-6">
          {/* Transaction Details */}
          <TransactionDetails trace={trace} />

          {/* Retry Info */}
          {trace.retry_count > 0 && <RetryInfo trace={trace} />}
        </div>
      </div>
    </div>
  )
}
