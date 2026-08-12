/**
 * Transaction list component
 */

'use client'

import Link from 'next/link'
import { format } from 'date-fns'

interface TransactionListProps {
  transactions: any[]
  loading: boolean
}

export default function TransactionList({ transactions, loading }: TransactionListProps) {
  if (loading) {
    return <div className="card text-slate-400">Loading transactions...</div>
  }

  if (!transactions || transactions.length === 0) {
    return <div className="card text-slate-400">No transactions found</div>
  }

  return (
    <div className="card">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left text-xs font-medium text-slate-400 py-3 px-4">Transaction ID</th>
            <th className="text-left text-xs font-medium text-slate-400 py-3 px-4">Reference</th>
            <th className="text-left text-xs font-medium text-slate-400 py-3 px-4">Amount</th>
            <th className="text-left text-xs font-medium text-slate-400 py-3 px-4">Provider</th>
            <th className="text-left text-xs font-medium text-slate-400 py-3 px-4">State</th>
            <th className="text-left text-xs font-medium text-slate-400 py-3 px-4">Created</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id} className="border-b border-slate-700 hover:bg-slate-900 transition-colors">
              <td className="py-3 px-4">
                <Link href={`/transactions/${tx.id}`} className="text-blue-400 hover:text-blue-300 text-sm">
                  {tx.transaction_id}
                </Link>
              </td>
              <td className="py-3 px-4 text-sm text-slate-300">{tx.reference}</td>
              <td className="py-3 px-4 text-sm text-slate-300">{tx.amount}</td>
              <td className="py-3 px-4 text-sm text-slate-300">{tx.provider}</td>
              <td className="py-3 px-4">
                <span className="text-xs px-2 py-1 bg-blue-900 text-blue-200 rounded">
                  {tx.current_state}
                </span>
              </td>
              <td className="py-3 px-4 text-sm text-slate-400">
                {format(new Date(tx.created_at), 'MMM dd, HH:mm')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
