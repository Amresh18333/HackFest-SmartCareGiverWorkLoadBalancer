import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-primary border-t-transparent" />
    </div>
  )
}

export function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) return <LoadingScreen />
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return <Outlet />
}

export function ManagerRoute() {
  const { isManager, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!isManager) return <Navigate to="/me" replace />
  return <Outlet />
}

export function MemberRoute() {
  const { isManager, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (isManager) return <Navigate to="/manager" replace />
  return <Outlet />
}

export function RoleHome() {
  const { isAuthenticated, isManager, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Navigate to={isManager ? '/manager' : '/me'} replace />
}
