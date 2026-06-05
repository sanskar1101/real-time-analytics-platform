'use client'

import Link from 'next/link'
import { useDashboard, useWidgets } from '../../../hooks/useDashboards'
import { useWebSocket } from '../../../hooks/useWebSocket'
import { WidgetGrid } from '../../../components/widgets/WidgetGrid'
import { Badge } from '../../../components/ui/badge'
import { Skeleton } from '../../../components/ui/skeleton'

interface Props {
  id: string
}

export function DashboardDetail({ id }: Props) {
  useWebSocket()

  const { data: dashboard, isPending: dashboardPending, isError: dashboardError } = useDashboard(id)
  const { data: widgets, isPending: widgetsPending, isError: widgetsError } = useWidgets(id)

  if (dashboardError) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/20">
        <p className="text-sm text-red-600 dark:text-red-400">
          Dashboard not found or you don&apos;t have access.
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-2 flex items-center gap-2 text-xs text-zinc-400">
        <Link href="/dashboard" className="hover:text-zinc-600 dark:hover:text-zinc-300">
          Dashboards
        </Link>
        <span>/</span>
        {dashboardPending ? (
          <Skeleton className="h-3 w-24" />
        ) : (
          <span className="text-zinc-600 dark:text-zinc-300">{dashboard?.name}</span>
        )}
      </div>

      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          {dashboardPending ? (
            <>
              <Skeleton className="mb-2 h-7 w-48" />
              <Skeleton className="h-4 w-72" />
            </>
          ) : (
            <>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
                  {dashboard?.name}
                </h1>
                {dashboard?.is_public && <Badge variant="secondary">Public</Badge>}
              </div>
              {dashboard?.description && (
                <p className="mt-1 text-sm text-zinc-500">{dashboard.description}</p>
              )}
            </>
          )}
        </div>
        {!dashboardPending && dashboard && (
          <p className="shrink-0 text-xs text-zinc-400">
            Created {new Date(dashboard.created_at).toLocaleDateString()}
          </p>
        )}
      </div>

      {widgetsPending && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
              <Skeleton className="mb-4 h-4 w-1/2" />
              <Skeleton className="h-32 w-full" />
            </div>
          ))}
        </div>
      )}

      {widgetsError && (
        <div className="flex h-32 items-center justify-center rounded-xl border border-dashed border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/20">
          <p className="text-sm text-red-600 dark:text-red-400">Failed to load widgets.</p>
        </div>
      )}

      {widgets && <WidgetGrid widgets={widgets} />}
    </div>
  )
}
