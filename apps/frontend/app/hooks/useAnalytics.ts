'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { EventCountResponse, EventsByDayResponse, EventsByTypeResponse } from '../types'

interface DateRange {
  start_date?: string
  end_date?: string
}

export function useEventCount(range?: DateRange) {
  return useQuery<EventCountResponse>({
    queryKey: ['analytics', 'event-count', range],
    queryFn: async () => {
      const { data } = await api.get('/analytics/event-count', { params: range })
      return data
    },
  })
}

export function useEventsByDay(range?: DateRange) {
  return useQuery<EventsByDayResponse>({
    queryKey: ['analytics', 'events-by-day', range],
    queryFn: async () => {
      const { data } = await api.get('/analytics/events-by-day', { params: range })
      return data
    },
  })
}

export function useEventsByType(range?: DateRange) {
  return useQuery<EventsByTypeResponse>({
    queryKey: ['analytics', 'events-by-type', range],
    queryFn: async () => {
      const { data } = await api.get('/analytics/events-by-type', { params: range })
      return data
    },
  })
}
