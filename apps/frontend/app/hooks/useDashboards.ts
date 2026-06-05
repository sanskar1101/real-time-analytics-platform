'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Dashboard, PaginatedDashboards, Widget } from '../types'

export function useDashboards(limit = 20, offset = 0) {
  return useQuery<PaginatedDashboards>({
    queryKey: ['dashboards', { limit, offset }],
    queryFn: async () => {
      const { data } = await api.get('/dashboards', { params: { limit, offset } })
      return data
    },
  })
}

export function useDashboard(id: string) {
  return useQuery<Dashboard>({
    queryKey: ['dashboards', id],
    queryFn: async () => {
      const { data } = await api.get(`/dashboards/${id}`)
      return data
    },
    enabled: Boolean(id),
  })
}

export function useWidgets(dashboardId: string) {
  return useQuery<Widget[]>({
    queryKey: ['dashboards', dashboardId, 'widgets'],
    queryFn: async () => {
      const { data } = await api.get(`/dashboards/${dashboardId}/widgets`)
      return data
    },
    enabled: Boolean(dashboardId),
  })
}
