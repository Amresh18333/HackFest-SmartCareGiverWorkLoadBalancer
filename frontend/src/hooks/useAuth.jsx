import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { auth, apiLogin, apiRegister, apiGetMe, apiCreateTeam, apiJoinTeam, apiGetMyTeam } from '../lib/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [loading, setLoading] = useState(true)
  
  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password)
    auth.setToken(data.access_token)
    auth.setMember(data.member)
    return data
  }, [])
  
  const register = useCallback(async (data) => {
    const result = await apiRegister(data)
    auth.setToken(result.access_token)
    auth.setMember(result.member)
    return result
  }, [])
  
  const logout = useCallback(() => {
    auth.clear()
  }, [])
  
  const createTeam = useCallback(async (teamName) => {
    return apiCreateTeam(teamName)
  }, [])
  
  const joinTeam = useCallback(async (joinCode) => {
    return apiJoinTeam(joinCode)
  }, [])
  
  const refreshTeam = useCallback(async () => {
    return apiGetMyTeam()
  }, [])
  
  const refreshMember = useCallback(async () => {
    const data = await apiGetMe()
    auth.setMember(data)
    return data
  }, [])
  
  useEffect(() => {
    const loaded = auth.loadFromStorage()
    if (loaded) {
      // Optionally refresh member data
      apiGetMe().catch(() => {})
    }
    setLoading(false)
  }, [])
  
  const value = {
    member: auth.member,
    token: auth.token,
    loading,
    login,
    register,
    logout,
    createTeam,
    joinTeam,
    refreshTeam,
    refreshMember,
    isAuthenticated: auth.isAuthenticated(),
    isManager: auth.isManager(),
  }
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}