import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { Button } from '../components/Button'
import { Avatar } from '../components/Avatar'

export function Login() {
  const navigate = useNavigate()
  const { login, register } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [avatarInitials, setAvatarInitials] = useState('')
  const [isManager, setIsManager] = useState(false)
  const [teamName, setTeamName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const getInitials = (n) => {
    return n.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    try {
      if (isLogin) {
        await login(email, password)
      } else {
        const data = {
          email,
          password,
          name,
          avatar_initials: avatarInitials || getInitials(name),
        }
        if (isManager) {
          data.is_manager = true
          data.team_name = teamName || `${name}'s Team`
        }
        await register(data)
      }
      navigate(isLogin ? '/' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
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
              {isLogin ? 'Sign in to your team dashboard' : 'Join or create a team'}
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
                    checked={isManager}
                    onChange={(e) => setIsManager(e.target.checked)}
                    className="w-4 h-4 text-brand-primary rounded border-[#D4D0DB] focus:ring-brand-primary"
                  />
                  <span className="text-sm text-text-primary">
                    I'm a manager - create a new team
                  </span>
                </label>
                
                {isManager && (
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
                )}
              </div>
            )}
            
            <Button 
              type="submit" 
              variant="primary" 
              className="w-full"
              loading={loading}
            >
              {isLogin ? 'Sign in' : 'Create account'}
            </Button>
          </form>
          
          <p className="text-center text-sm text-text-muted mt-6">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="ml-2 text-brand-primary hover:underline font-medium"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
          
          {!isLogin && (
            <div className="mt-6 p-4 bg-[#F7F5FA] rounded-lg">
              <p className="text-sm text-text-muted text-center">
                <strong>Joining a team?</strong> Create your account first, then use the 
                join code from your manager to join their team.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}