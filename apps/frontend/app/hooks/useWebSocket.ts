'use client'

import { useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { getWsUrl } from '../lib/api'
import type { WsNotification } from '../types'

const RECONNECT_DELAY_MS = 3_000
const MAX_RECONNECT_ATTEMPTS = 10

export function useWebSocket(enabled = true) {
  const queryClient = useQueryClient()
  const wsRef = useRef<WebSocket | null>(null)
  const attemptsRef = useRef(0)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!enabled) return

    function connect() {
      const url = getWsUrl()
      if (!url.includes('token=')) return

      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        attemptsRef.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const notification: WsNotification = JSON.parse(event.data)
          if (notification.type === 'notification') {
            queryClient.invalidateQueries({ queryKey: ['analytics'] })
            queryClient.invalidateQueries({ queryKey: ['dashboards'] })
          }
        } catch {
          // ignore malformed frames
        }
      }

      ws.onclose = () => {
        if (attemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          attemptsRef.current += 1
          timerRef.current = setTimeout(connect, RECONNECT_DELAY_MS)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      wsRef.current?.close()
    }
  }, [enabled, queryClient])
}
