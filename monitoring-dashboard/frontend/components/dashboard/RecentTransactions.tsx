/**
 * Recent transactions list
 */

'use client'

import { useDashboardStore } from '@/store/dashboard'
import Link from 'next/link'
import { ExternalLink } from 'lucide-react'

export default function RecentTransactions() {
  const { transactions } = useDashboardStore()

  if (!transactions || transactions.length === 0) {
    return <div className="card text-slate-400">No transactions yet</div>
  }

  const recent = transactions.slice(0, 5)

  return (
    <div className="card">
      <p className="card-title">Recent Transactions</p>
      <div className="space-y-3">
        {recent.map((tx) => (
          <div key={tx.id} className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-200">{tx.transaction_id}</p>
              <p className="text-xs text-slate-400 mt-1">
                {tx.provider} • {tx.amount}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs px-2 py-1 bg-blue-900 text-blue-200 rounded">
                {tx.current_state}
              </span>
              <Link href={`/transactions/${tx.id}`} className="text-slate-400 hover:text-slate-200">
                <ExternalLink size={16} />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
