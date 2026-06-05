'use client'

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useEventsByDay } from '../../hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Skeleton } from '../ui/skeleton'
import type { Widget } from '../../types'

interface Props {
  widget: Widget
}

export function LineChartWidget({ widget }: Props) {
  const { data, isPending, isError } = useEventsByDay()

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
            <LineChart data={data.items} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: '#71717a' }}
                tickFormatter={(v: string) => v.slice(5)}
              />
              <YAxis tick={{ fontSize: 11, fill: '#71717a' }} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e4e4e7' }}
                labelStyle={{ fontWeight: 600 }}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
