/**
 * Custom hook for WebSocket integration
 */

import { useEffect, useCallback } from 'react'
import { wsClient } from '@/lib/websocket'

export function useWebSocket(event: string, handler: (data: any) => void) {
  const memoizedHandler = useCallback(handler, [handler])

  useEffect(() => {
    wsClient.subscribe(event, memoizedHandler)

    return () => {
      wsClient.unsubscribe(event, memoizedHandler)
    }
  }, [event, memoizedHandler])
}

export function useWebSocketConnect() {
  useEffect(() => {
    wsClient.connect().catch((error) => {
      console.error('Failed to connect WebSocket:', error)
    })

    return () => {
      // Don't disconnect on unmount to keep updates flowing
    }
  }, [])
}
