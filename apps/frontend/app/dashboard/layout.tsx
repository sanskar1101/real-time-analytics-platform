import Link from 'next/link'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/80">
        <div className="mx-auto flex h-14 max-w-screen-xl items-center gap-4 px-4 sm:px-6">
          <Link href="/dashboard" className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
            Analytics
          </Link>
          <span className="text-zinc-300 dark:text-zinc-700">/</span>
          <nav className="flex items-center gap-4 text-sm text-zinc-500">
            <Link
              href="/dashboard"
              className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-50"
            >
              Dashboards
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-screen-xl px-4 py-8 sm:px-6">{children}</main>
    </div>
  )
}
