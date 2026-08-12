/**
 * Transaction search component
 */

'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'

interface TransactionSearchProps {
  onFilterChange: (filter: any) => void
}

export default function TransactionSearch({ onFilterChange }: TransactionSearchProps) {
  const [search, setSearch] = useState('')
  const [state, setState] = useState('')
  const [provider, setProvider] = useState('')

  const handleSearchChange = (value: string) => {
    setSearch(value)
    onFilterChange({ search: value, state, provider })
  }

  const handleStateChange = (value: string) => {
    setState(value)
    onFilterChange({ search, state: value, provider })
  }

  const handleProviderChange = (value: string) => {
    setProvider(value)
    onFilterChange({ search, state, provider: value })
  }

  return (
    <div className="card">
      <div className="grid grid-cols-3 gap-4">
        {/* Search */}
        <div className="relative">
          <Search size={18} className="absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Transaction ID or reference..."
            className="w-full bg-slate-900 text-slate-100 pl-10 pr-4 py-2 rounded-lg border border-slate-700 focus:border-blue-500 outline-none"
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
        </div>

        {/* State Filter */}
        <select
          value={state}
          onChange={(e) => handleStateChange(e.target.value)}
          className="bg-slate-900 text-slate-100 px-4 py-2 rounded-lg border border-slate-700 focus:border-blue-500 outline-none"
        >
          <option value="">All States</option>
          <option value="INITIATED">Initiated</option>
          <option value="AUTHORIZED">Authorized</option>
          <option value="PROCESSING">Processing</option>
          <option value="SETTLED">Settled</option>
          <option value="FAILED">Failed</option>
        </select>

        {/* Provider Filter */}
        <select
          value={provider}
          onChange={(e) => handleProviderChange(e.target.value)}
          className="bg-slate-900 text-slate-100 px-4 py-2 rounded-lg border border-slate-700 focus:border-blue-500 outline-none"
        >
          <option value="">All Providers</option>
          <option value="NIBSS">NIBSS</option>
          <option value="Paystack">Paystack</option>
          <option value="Flutterwave">Flutterwave</option>
        </select>
      </div>
    </div>
  )
}
