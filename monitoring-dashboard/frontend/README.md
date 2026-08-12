# Frontend

Real-time monitoring dashboard built with Next.js, React, and Tailwind CSS.

## Features

- Real-time transaction metrics and status
- Transaction search and filtering
- Detailed transaction trace visualization
- Alert management and notifications
- Service health monitoring
- Queue metrics and performance data
- WebSocket-based real-time updates

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

## Pages

- `/` - Dashboard overview with key metrics
- `/transactions` - Search and explore transactions
- `/transactions/:id` - Transaction details and trace
- `/alerts` - Alert history and summary
- `/health` - System health and infrastructure status

## Components

### Dashboard
- MetricsGrid: Key performance indicators
- TransactionStateChart: Transaction state distribution
- RecentTransactions: Latest transaction list
- AlertsPanel: Active alerts summary
- ServiceHealth: Service status

### Transactions
- TransactionSearch: Search and filter controls
- TransactionList: Paginated transaction table

### Trace
- TransactionTimeline: Event timeline visualization
- TransactionDetails: Transaction metadata
- RetryInfo: Retry attempt details

### Alerts
- AlertsList: Alert history with filtering
- AlertsSummary: Alert severity summary

### Health
- ServiceStatus: Service availability status
- DatabaseHealth: Database connection and performance
- QueueMetrics: Message queue depth and throughput

## Configuration

Environment variables in `.env.local`:
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL (default: http://localhost:8001)
- `NEXT_PUBLIC_WS_URL`: WebSocket server URL (default: ws://localhost:8001)

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: React 18 with Tailwind CSS
- **State**: Zustand
- **Charts**: Recharts
- **HTTP**: Axios
- **Icons**: Lucide React
- **Utilities**: date-fns
