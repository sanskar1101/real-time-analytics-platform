import { DashboardDetail } from './_components/DashboardDetail'

interface Props {
  params: Promise<{ id: string }>
}

export default async function DashboardDetailPage({ params }: Props) {
  const { id } = await params
  return <DashboardDetail id={id} />
}
