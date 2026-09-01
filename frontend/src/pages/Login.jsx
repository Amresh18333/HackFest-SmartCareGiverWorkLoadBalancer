import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { Button } from '../components/Button'
import { Avatar } from '../components/Avatar'

function destForRole(role) {
  return role === 'manager' ? '/manager' : '/me'
}

export function Login() {
  const navigate = useNavigate()
  const { login, register, isAuthenticated, isManager, loading } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [avatarInitials, setAvatarInitials] = useState('')
  const [isManagerSignup, setIsManagerSignup] = useState(false)
  const [teamName, setTeamName] = useState('')
  const [joinCode, setJoinCode] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const getInitials = (n) => {
    return n.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
  }

  if (!loading && isAuthenticated) {
    return <Navigate to={isManager ? '/manager' : '/me'} replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      if (isLogin) {
        const data = await login(email, password)
        navigate(data.redirect || destForRole(data.member?.role), { replace: true })
      } else {
        const payload = {
          email,
          password,
          name,
          avatar_initials: avatarInitials || getInitials(name),
        }
        if (isManagerSignup) {
          payload.is_manager = true
          payload.team_name = teamName || `${name}'s Team`
        } else if (joinCode.trim()) {
          payload.join_code = joinCode.trim().toUpperCase()
        }
        const data = await register(payload)
        navigate(data.redirect || destForRole(data.member?.role), { replace: true })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="card p-8">
          <div className="text-center mb-8">
            <Avatar
              initials={isLogin ? 'WB' : '+'}
              size="xl"
              className="mx-auto mb-4 bg-brand-primary/20"
            />
            <h1 className="text-2xl font-bold text-text-primary">
              {isLogin ? 'Welcome back' : 'Create account'}
            </h1>
            <p className="text-text-muted mt-2">
              {isLogin ? 'Sign in — we send you to the dashboard for your role' : 'Join a team or create one as a manager'}
            </p>
          </div>

          {error && (
            <div className="toast-error mb-6 p-3 rounded-lg bg-risk-high/10 text-risk-high text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value)
                    setAvatarInitials(getInitials(e.target.value))
                  }}
                  className="input"
                  placeholder="Alex Chen"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="alex@team.com"
                required
                autoComplete="email"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="••••••••"
                required
                autoComplete={isLogin ? 'current-password' : 'new-password'}
              />
            </div>

            {!isLogin && (
              <div className="space-y-3 border-t pt-4 border-[#EDEAF1]">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isManagerSignup}
                    onChange={(e) => setIsManagerSignup(e.target.checked)}
                    className="w-4 h-4 text-brand-primary rounded border-[#D4D0DB] focus:ring-brand-primary"
                  />
                  <span className="text-sm text-text-primary">
                    I'm a manager — create a new team
                  </span>
                </label>

                {isManagerSignup ? (
                  <div className="ml-6">
                    <label className="block text-sm font-medium text-text-primary mb-1">
                      Team Name
                    </label>
                    <input
                      type="text"
                      value={teamName}
                      onChange={(e) => setTeamName(e.target.value)}
                      className="input"
                      placeholder="Care Team Alpha"
                    />
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-1">
                      Team join code (optional)
                    </label>
                    <input
                      type="text"
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                      className="input uppercase"
                      placeholder="ABC123EF"
                      maxLength={8}
                    />
                  </div>
                )}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={submitting}
            >
              {isLogin ? 'Sign in' : 'Create account'}
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setError('')
              }}
              className="ml-2 text-brand-primary hover:underline font-medium"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
