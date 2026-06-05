export type WidgetType = 'KPI' | 'LINE' | 'BAR' | 'PIE'
export type MetricType = 'EVENT_COUNT' | 'EVENTS_BY_DAY' | 'EVENTS_BY_TYPE'

export interface Dashboard {
  id: string
  organization_id: string
  name: string
  description: string | null
  is_public: boolean
  created_at: string
}

export interface PaginatedDashboards {
  items: Dashboard[]
  total: number
  limit: number
  offset: number
}

export interface Widget {
  id: string
  dashboard_id: string
  name: string
  widget_type: WidgetType
  metric_type: MetricType
  time_range: string | null
  position_x: number
  position_y: number
  width: number
  height: number
  created_at: string
}

export interface EventCountResponse {
  total: number
}

export interface EventsByDayItem {
  date: string
  count: number
}

export interface EventsByDayResponse {
  items: EventsByDayItem[]
}

export interface EventsByTypeItem {
  event_name: string
  count: number
}

export interface EventsByTypeResponse {
  items: EventsByTypeItem[]
}

export interface WsNotification {
  type: string
  id: string
  title: string
  message: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
