'use client'

import { useEventCount } from '../../hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Skeleton } from '../ui/skeleton'
import type { Widget } from '../../types'

interface Props {
  widget: Widget
}

export function KpiWidget({ widget }: Props) {
  const { data, isPending, isError } = useEventCount()

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>{widget.name}</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending && <Skeleton className="h-10 w-32" />}
        {isError && <p className="text-sm text-red-500">Failed to load</p>}
        {data && (
          <div className="flex flex-col gap-1">
            <span className="text-4xl font-bold tabular-nums text-zinc-900 dark:text-zinc-50">
              {data.total.toLocaleString()}
            </span>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">total events</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
