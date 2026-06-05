'use client'

import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { useEventsByType } from '../../hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Skeleton } from '../ui/skeleton'
import type { Widget } from '../../types'

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444']

interface Props {
  widget: Widget
}

export function PieChartWidget({ widget }: Props) {
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
            <PieChart>
              <Pie
                data={data.items}
                dataKey="count"
                nameKey="event_name"
                cx="50%"
                cy="50%"
                outerRadius={64}
                innerRadius={32}
              >
                {data.items.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e4e4e7' }}
              />
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(value) => (
                  <span style={{ fontSize: 11, color: '#71717a' }}>{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
