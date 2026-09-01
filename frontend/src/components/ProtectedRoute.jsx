import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

export function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, isManager, loading } = useAuth()
  const location = useLocation()
  
  if (loading) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-primary border-t-transparent"></div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  
  if (allowedRoles && !allowedRoles.includes(isManager ? 'manager' : 'member')) {
    return <Navigate to="/" replace />
  }
  
  return children
}

export function ManagerRoute({ children }) {
  return <ProtectedRoute allowedRoles={['manager']}>{children}</ProtectedRoute>
}

export function MemberRoute({ children }) {
  return <ProtectedRoute allowedRoles={['member']}>{children}</ProtectedRoute>
}