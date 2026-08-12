/**
 * Transactions page
 */

'use client'

import { useEffect, useState } from 'react'
import TransactionSearch from '@/components/transactions/TransactionSearch'
import TransactionList from '@/components/transactions/TransactionList'
import { fetchTransactions } from '@/lib/api'

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ state: '', provider: '', search: '' })

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        setLoading(true)
        const data = await fetchTransactions()
        setTransactions(data)
      } catch (error) {
        console.error('Failed to load transactions:', error)
      } finally {
        setLoading(false)
      }
    }

    loadTransactions()
  }, [filter])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Transactions</h1>
        <p className="text-slate-400 mt-1">Search and explore transaction details</p>
      </div>

      <TransactionSearch onFilterChange={setFilter} />
      <TransactionList transactions={transactions} loading={loading} />
    </div>
  )
}
