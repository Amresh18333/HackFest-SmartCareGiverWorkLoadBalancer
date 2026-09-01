import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { apiGetMyTasks, apiUpdateTaskStatus, apiSubmitSignals, apiGetMyRisk, apiGetMyTeam, apiJoinTeam } from '../lib/auth'
import { RiskScoreDisplay } from '../components/RiskScoreDisplay'
import { RiskTrendChart } from '../components/RiskTrendChart'
import { TaskList } from '../components/TaskList'
import { Avatar } from '../components/Avatar'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { ToastContainer, showToast } from '../components/Toast'

export function MemberDashboard() {
  const { member, refreshMember, refreshTeam, isAuthenticated } = useAuth()
  const [tasks, setTasks] = useState([])
  const [risk, setRisk] = useState(null)
  const [team, setTeam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [signalLoading, setSignalLoading] = useState(false)
  
  const [signals, setSignals] = useState({
    self_checkin_score: 3,
    tasks_today: 0,
    late_night_activity_flag: false,
    avg_response_latency_mins: 30,
  })
  
  useEffect(() => {
    if (!isAuthenticated) return
    
    const loadData = async () => {
      setLoading(true)
      try {
        const [tasksData, riskData, teamData] = await Promise.all([
          apiGetMyTasks(),
          apiGetMyRisk(),
          apiGetMyTeam(),
        ])
        setTasks(tasksData)
        setRisk(riskData)
        setTeam(teamData)
        
        const activeTasks = tasksData.filter(t => t.status !== 'done').length
        setSignals(prev => ({ ...prev, tasks_today: activeTasks }))
      } catch (err) {
        console.error('Failed to load member data:', err)
        showToast(err.message, 'error')
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
  }, [isAuthenticated])
  
  const getRiskLevel = (score) => {
    if (score < 40) return 'low'
    if (score < 70) return 'medium'
    return 'high'
  }
  
  const riskColors = {
    low: '#7FA98D',
    medium: '#E8A94C',
    high: '#D2685F',
  }
  
  const handleTaskStatusChange = async (task, newStatus) => {
    try {
      await apiUpdateTaskStatus(task.id, newStatus)
      setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: newStatus } : t))
      showToast(`Task marked as ${newStatus.replace('_', ' ')}`, 'success')
    } catch (err) {
      showToast(err.message, 'error')
    }
  }
  
  const handleSubmitSignals = async (e) => {
    e.preventDefault()
    setSignalLoading(true)
    try {
      const data = await apiSubmitSignals(signals)
      showToast('Daily check-in submitted', 'success')
      const riskData = await apiGetMyRisk()
      setRisk(riskData)
      await refreshMember()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setSignalLoading(false)
    }
  }
  
  const handleJoinTeam = async (joinCode) => {
    try {
      await apiJoinTeam(joinCode)
      showToast('Joined team successfully!', 'success')
      await refreshTeam()
      const teamData = await apiGetMyTeam()
      setTeam(teamData)
    } catch (err) {
      showToast(err.message, 'error')
    }
  }
  
  if (loading) {
    return (
      <div className="page-container">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-[#EDEAF1] rounded w-1/4" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-64 bg-[#EDEAF1] rounded lg:col-span-2" />
            <div className="h-64 bg-[#EDEAF1] rounded" />
          </div>
        </div>
      </div>
    )
  }
  
  const currentScore = risk?.current_score || 0
  const riskLevel = getRiskLevel(currentScore)
  const riskColor = riskColors[riskLevel]
  const incompleteTasks = tasks.filter(t => t.status !== 'done')
  const completedTasks = tasks.filter(t => t.status === 'done')
  const totalHours = tasks.reduce((sum, t) => sum + (t.estimated_hours || 0), 0)
  
  return (
    <div className="page-container">
      <ToastContainer />
      
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <Avatar initials={member?.avatar_initials || '?'} size="xl" />
            <div>
              <h1 className="text-2xl font-bold text-text-primary">
                Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {member?.name?.split(' ')[0] || 'there'}
              </h1>
              <p className="text-text-muted">Your personal workload dashboard</p>
            </div>
          </div>
          
          {!team?.team && (
            <div className="card p-4 bg-brand-primary/5 border-l-4 border-brand-primary max-w-md">
              <p className="text-sm text-text-muted mb-2">Not part of a team yet?</p>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter join code (e.g. ABC123EF)"
                  className="input flex-1 text-uppercase"
                  maxLength={8}
                  id="join-code-input"
                />
                <Button onClick={() => handleJoinTeam(document.getElementById('join-code-input')?.value)}>
                  Join Team
                </Button>
              </div>
            </div>
          )}
        </div>
        
        {/* Team info if joined */}
        {team?.team && (
          <div className="card p-4 mb-6 bg-brand-primary/5 border-l-4 border-brand-primary">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-brand-primary/20 flex items-center justify-center">
                  <span className="text-brand-primary font-bold">{team.team.name[0]}</span>
                </div>
                <div>
                  <p className="font-medium text-text-primary">{team.team.name}</p>
                  <p className="text-sm text-text-muted">Your join code: <code className="font-mono text-brand-primary">{team.team.join_code}</code></p>
                </div>
              </div>
              <Badge variant="low">{team.members?.length || 0} members</Badge>
            </div>
          </div>
        )}
      </header>
      
      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Risk & Tasks */}
        <div className="lg:col-span-2 space-y-6">
          {/* Risk Score Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-text-primary">Your Burnout Risk</h2>
              <Badge variant={riskLevel}>{riskLevel} risk</Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Risk Gauge */}
              <div className="flex flex-col items-center justify-center py-4">
                <div className="relative w-48 h-48">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      fill="none"
                      stroke="#EDEAF1"
                      strokeWidth="12"
                    />
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      fill="none"
                      stroke={riskColor}
                      strokeWidth="12"
                      strokeLinecap="round"
                      strokeDasharray={`${(currentScore / 100) * 553} 553`}
                      className="transition-all duration-1000"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <RiskScoreDisplay score={currentScore} size="lg" showLabel={true} />
                    <p className="text-sm text-text-muted mt-2">Updated today</p>
                  </div>
                </div>
              </div>
              
              {/* Key Drivers */}
              <div>
                <h3 className="font-medium text-text-primary mb-4">What's driving this</h3>
                {risk?.top_drivers?.length > 0 ? (
                  <div className="space-y-3">
                    {risk.top_drivers.map((driver, i) => (
                      <div key={i} className="flex items-center gap-3 p-3 bg-[#F7F5FA] rounded-lg">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: riskColor }} />
                        <span className="text-text-primary">{driver}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-text-muted">Complete your daily check-in to see drivers</p>
                )}
              </div>
            </div>
            
            {/* Risk Trend */}
            {risk?.score_history?.length > 0 && (
              <div className="mt-6 pt-6 border-t border-[#EDEAF1]">
                <h3 className="font-medium text-text-primary mb-4">30-Day Trend</h3>
                <RiskTrendChart data={risk.score_history} height={200} />
              </div>
            )}
          </div>
          
          {/* Tasks */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Today's Tasks</h2>
              <div className="flex items-center gap-4 text-sm text-text-muted">
                <span>{incompleteTasks.length} active</span>
                <span>•</span>
                <span>{completedTasks.length} done</span>
                <span>•</span>
                <span>{totalHours.toFixed(1)}h total</span>
              </div>
            </div>
            
            <TaskList 
              tasks={tasks} 
              onReassign={null}
              onStatusChange={handleTaskStatusChange}
              showAssignee={false}
            />
          </div>
        </div>
        
        {/* Right Column - Daily Check-in */}
        <div className="space-y-6">
          {/* Daily Check-in Card */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4">Daily Check-in</h2>
            <p className="text-sm text-text-muted mb-6">
              Help the team understand your capacity today. Takes 30 seconds.
            </p>
            
            <form onSubmit={handleSubmitSignals} className="space-y-4">
              {/* Self Check-in */}
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  How are you feeling today?
                </label>
                <div className="flex gap-2">
                  {[1,2,3,4,5].map(level => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setSignals(prev => ({ ...prev, self_checkin_score: level }))}
                      className={`flex-1 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        signals.self_checkin_score === level
                          ? 'border-risk-high bg-risk-high/10 text-risk-high'
                          : 'border-[#D4D0DB] text-text-muted hover:border-brand-primary'
                      }`}
                    >
                      {['😰','😟','😐','🙂','😊'][level-1]} {['Struggling','Tough','Okay','Good','Great'][level-1]}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Tasks Today */}
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Tasks today <span className="text-risk-high">*</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  value={signals.tasks_today}
                  onChange={(e) => setSignals(prev => ({ ...prev, tasks_today: parseInt(e.target.value) || 0 }))}
                  className="input"
                />
              </div>
              
              {/* Late Night */}
              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={signals.late_night_activity_flag}
                    onChange={(e) => setSignals(prev => ({ ...prev, late_night_activity_flag: e.target.checked }))}
                    className="w-4 h-4 text-brand-primary rounded border-[#D4D0DB] focus:ring-brand-primary"
                  />
                  <span className="text-sm text-text-primary">I worked late last night (after 10 PM)</span>
                </label>
              </div>
              
              {/* Response Latency */}
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Avg response time (minutes)
                </label>
                <input
                  type="number"
                  min="0"
                  max="500"
                  value={signals.avg_response_latency_mins}
                  onChange={(e) => setSignals(prev => ({ ...prev, avg_response_latency_mins: parseInt(e.target.value) || 0 }))}
                  className="input"
                />
              </div>
              
              <Button 
                type="submit" 
                variant="primary" 
                className="w-full"
                loading={signalLoading}
              >
                Submit Check-in
              </Button>
            </form>
          </div>
          
          {/* Team Join (if no team) */}
          {!team?.team && (
            <div className="card p-6 text-center">
              <div className="w-16 h-16 rounded-full bg-brand-primary/20 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-brand-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-text-primary mb-2">Join a Team</h3>
              <p className="text-text-muted mb-4">Ask your manager for a join code to connect with your team</p>
              <div className="flex gap-2 max-w-xs mx-auto">
                <input
                  type="text"
                  placeholder="ABC123EF"
                  className="input text-uppercase text-center"
                  maxLength={8}
                  id="join-code-input"
                />
                <Button onClick={() => handleJoinTeam(document.getElementById('join-code-input')?.value)}>
                  Join
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}