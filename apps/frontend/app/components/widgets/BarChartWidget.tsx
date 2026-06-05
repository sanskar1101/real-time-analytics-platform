'use client'

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useEventsByType } from '../../hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Skeleton } from '../ui/skeleton'
import type { Widget } from '../../types'

interface Props {
  widget: Widget
}

export function BarChartWidget({ widget }: Props) {
  const { data, isPending, isError } = useEventsByType()

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>{widget.name}</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && <Skeleton className="h-48 w-full" />}
        {isError && <p className="text-sm text-red-500">Failed to load</p>}
        {data && (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data.items} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
              <XAxis
                dataKey="event_name"
                tick={{ fontSize: 11, fill: '#71717a' }}
                interval={0}
                angle={-30}
                textAnchor="end"
                height={40}
              />
              <YAxis tick={{ fontSize: 11, fill: '#71717a' }} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e4e4e7' }}
              />
              <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
