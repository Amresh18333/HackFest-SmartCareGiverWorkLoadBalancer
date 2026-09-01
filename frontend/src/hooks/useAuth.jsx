import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react'
import { auth, apiLogin, apiRegister, apiGetMe, apiCreateTeam, apiJoinTeam, apiGetMyTeam } from '../lib/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [member, setMember] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  const applySession = useCallback((accessToken, memberData) => {
    auth.setToken(accessToken)
    auth.setMember(memberData)
    setToken(accessToken)
    setMember(memberData)
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password)
    applySession(data.access_token, data.member)
    return data
  }, [applySession])

  const register = useCallback(async (payload) => {
    const result = await apiRegister(payload)
    applySession(result.access_token, result.member)
    return result
  }, [applySession])

  const logout = useCallback(() => {
    auth.clear()
    setToken(null)
    setMember(null)
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
    setMember(data)
    return data
  }, [])

  useEffect(() => {
    const loaded = auth.loadFromStorage()
    if (loaded) {
      setToken(auth.token)
      setMember(auth.member)
      apiGetMe()
        .then((data) => {
          auth.setMember(data)
          setMember(data)
        })
        .catch(() => {
          auth.clear()
          setToken(null)
          setMember(null)
        })
        .finally(() => setLoading(false))
      return
    }
    setLoading(false)
  }, [])

  const value = useMemo(() => ({
    member,
    token,
    loading,
    login,
    register,
    logout,
    createTeam,
    joinTeam,
    refreshTeam,
    refreshMember,
    isAuthenticated: !!(token && member),
    isManager: member?.role === 'manager',
  }), [member, token, loading, login, register, logout, createTeam, joinTeam, refreshTeam, refreshMember])

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
