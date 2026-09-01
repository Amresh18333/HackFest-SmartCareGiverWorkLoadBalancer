import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth.jsx'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { MemberDetail } from './pages/MemberDetail'
import { MemberDashboard } from './pages/MemberDashboard'
import { ProtectedRoute, ManagerRoute, MemberRoute } from './components/ProtectedRoute'

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      
      {/* Protected routes - role based */}
      <Route
        element={
          <ProtectedRoute>
            <Navigate to="/manager" replace />
          </ProtectedRoute>
        }
      >
        {/* Manager routes */}
        <Route
          element={<ManagerRoute><Navigate to="/manager" replace /></ManagerRoute>}
        >
          <Route path="/manager" element={<Dashboard />} />
          <Route path="/manager/member/:memberId" element={<MemberDetail />} />
        </Route>
        
        {/* Member routes */}
        <Route
          element={<MemberRoute><Navigate to="/me" replace /></MemberRoute>}
        >
          <Route path="/me" element={<MemberDashboard />} />
        </Route>
      </Route>
      
      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
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