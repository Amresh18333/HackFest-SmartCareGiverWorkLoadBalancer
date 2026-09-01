import { useAuth } from '../hooks/useAuth.jsx'
import { Button } from './Button'
import { Avatar } from './Avatar'

export function AppHeader({ title, subtitle, extra }) {
  const { member, logout } = useAuth()

  return (
    <header className="mb-8">
      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-4 min-w-0">
          <Avatar initials={member?.avatar_initials || '?'} size="lg" />
          <div className="min-w-0">
            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary truncate">{title}</h1>
            {subtitle && <p className="text-text-muted mt-1">{subtitle}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {extra}
          <Button variant="ghost" size="sm" onClick={logout}>
            Sign out
          </Button>
        </div>
      </div>
    </header>
  )
}
