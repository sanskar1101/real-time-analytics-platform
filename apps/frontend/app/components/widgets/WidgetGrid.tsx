'use client'

import type { Widget } from '../../types'
import { WidgetRenderer } from './WidgetRenderer'

interface Props {
  widgets: Widget[]
}

const COLS = 12
const ROW_HEIGHT = 120

export function WidgetGrid({ widgets }: Props) {
  if (widgets.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-zinc-300 dark:border-zinc-700">
        <p className="text-sm text-zinc-500">No widgets on this dashboard yet.</p>
      </div>
    )
  }

  const maxRow = widgets.reduce((acc, w) => Math.max(acc, w.position_y + w.height), 0)
  const gridHeight = maxRow * ROW_HEIGHT

  return (
    <div
      className="relative w-full"
      style={{ height: gridHeight, minHeight: 240 }}
    >
      {widgets.map((widget) => (
        <div
          key={widget.id}
          className="absolute p-2"
          style={{
            left: `${(widget.position_x / COLS) * 100}%`,
            top: widget.position_y * ROW_HEIGHT,
            width: `${(widget.width / COLS) * 100}%`,
            height: widget.height * ROW_HEIGHT,
          }}
        >
          <WidgetRenderer widget={widget} />
        </div>
      ))}
    </div>
  )
}
