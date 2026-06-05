'use client'

import type { Widget } from '../../types'
import { KpiWidget } from './KpiWidget'
import { LineChartWidget } from './LineChartWidget'
import { BarChartWidget } from './BarChartWidget'
import { PieChartWidget } from './PieChartWidget'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'

interface Props {
  widget: Widget
}

export function WidgetRenderer({ widget }: Props) {
  switch (widget.widget_type) {
    case 'KPI':
      return <KpiWidget widget={widget} />
    case 'LINE':
      return <LineChartWidget widget={widget} />
    case 'BAR':
      return <BarChartWidget widget={widget} />
    case 'PIE':
      return <PieChartWidget widget={widget} />
    default:
      return (
        <Card className="h-full">
          <CardHeader>
            <CardTitle>{widget.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-zinc-500">Unknown widget type</p>
          </CardContent>
        </Card>
      )
  }
}
