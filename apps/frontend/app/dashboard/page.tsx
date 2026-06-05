import { DashboardList } from './_components/DashboardList'

export const metadata = { title: 'Dashboards — Analytics' }

export default function DashboardsPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">Dashboards</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Select a dashboard to view its widgets and live analytics.
        </p>
      </div>
      <DashboardList />
    </div>
  )
}
