import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth.jsx'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { MemberDetail } from './pages/MemberDetail'
import { MemberDashboard } from './pages/MemberDashboard'
import { ProtectedRoute, ManagerRoute, MemberRoute, RoleHome } from './components/ProtectedRoute'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<ManagerRoute />}>
          <Route path="/manager" element={<Dashboard />} />
          <Route path="/manager/member/:memberId" element={<MemberDetail />} />
        </Route>

        <Route element={<MemberRoute />}>
          <Route path="/me" element={<MemberDashboard />} />
        </Route>
      </Route>

      <Route path="/" element={<RoleHome />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-bg">
        <AppRoutes />
      </div>
    </AuthProvider>
  )
}
