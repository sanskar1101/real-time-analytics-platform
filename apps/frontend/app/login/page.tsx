import { LoginForm } from './_components/LoginForm'

export const metadata = { title: 'Sign in — Analytics' }

interface Props {
  searchParams: Promise<{ redirect?: string }>
}

export default async function LoginPage({ searchParams }: Props) {
  const { redirect } = await searchParams
  const redirectTo = redirect && redirect.startsWith('/') ? redirect : '/dashboard'
  return <LoginForm redirectTo={redirectTo} />
}
