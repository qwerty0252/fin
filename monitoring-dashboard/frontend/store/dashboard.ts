/**
 * Zustand store for dashboard state
 */

import { create } from 'zustand'

interface DashboardState {
  metrics: any
  transactions: any[]
  alerts: any[]
  health: any
  setMetrics: (metrics: any) => void
  setTransactions: (transactions: any[]) => void
  setAlerts: (alerts: any[]) => void
  setHealth: (health: any) => void
}

export const useDashboardStore = create<DashboardState>((set) => ({
  metrics: null,
  transactions: [],
  alerts: [],
  health: null,
  setMetrics: (metrics) => set({ metrics }),
  setTransactions: (transactions) => set({ transactions }),
  setAlerts: (alerts) => set({ alerts }),
  setHealth: (health) => set({ health }),
}))
