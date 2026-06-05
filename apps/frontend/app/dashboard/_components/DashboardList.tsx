'use client'

import Link from 'next/link'
import { useDashboards } from '../../hooks/useDashboards'
import { useWebSocket } from '../../hooks/useWebSocket'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Badge } from '../../components/ui/badge'
import { Skeleton } from '../../components/ui/skeleton'

export function DashboardList() {
  useWebSocket()

  const { data, isPending, isError } = useDashboards()

  if (isPending) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-3 w-1/2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-3 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/20">
        <p className="text-sm text-red-600 dark:text-red-400">
          Failed to load dashboards. Check your connection or authentication.
        </p>
      </div>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-zinc-300 dark:border-zinc-700">
        <p className="text-sm text-zinc-500">No dashboards found.</p>
      </div>
    )
  }

  return (
    <>
      <p className="mb-6 text-sm text-zinc-500">{data.total} dashboard{data.total !== 1 ? 's' : ''}</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.items.map((dashboard) => (
          <Link key={dashboard.id} href={`/dashboard/${dashboard.id}`}>
            <Card className="h-full cursor-pointer transition-shadow hover:shadow-md">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="line-clamp-1">{dashboard.name}</CardTitle>
                  {dashboard.is_public && (
                    <Badge variant="secondary" className="shrink-0">
                      Public
                    </Badge>
                  )}
                </div>
                {dashboard.description && (
                  <CardDescription className="line-clamp-2">
                    {dashboard.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <p className="text-xs text-zinc-400">
                  Created {new Date(dashboard.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </>
  )
}
