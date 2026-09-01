import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMembers } from '../hooks/useMembers'
import { useAuth } from '../hooks/useAuth.jsx'
import { api } from '../lib/api'
import { Sparkline } from '../components/Sparkline'
import { RiskScoreDisplay } from '../components/RiskScoreDisplay'
import { Avatar } from '../components/Avatar'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { AppHeader } from '../components/AppHeader'
import { ToastContainer, showToast } from '../components/Toast'

export function Dashboard() {
  const { members, loading, error, refetch } = useMembers()
  const { member } = useAuth()
  const [summary, setSummary] = useState('')
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [team, setTeam] = useState(null)

  useEffect(() => {
    api.getMyTeam()
      .then(setTeam)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (members.length > 0 && !summary) {
      generateSummary()
    }
  }, [members])

  const generateSummary = async () => {
    setSummaryLoading(true)
    try {
      const highRisk = members.filter((m) => m.current_score >= 70).length
      const mediumRisk = members.filter((m) => m.current_score >= 40 && m.current_score < 70).length
      const lowRisk = members.filter((m) => m.current_score < 40).length

      const topConcerns = members
        .filter((m) => m.current_score >= 70)
        .sort((a, b) => b.current_score - a.current_score)
        .slice(0, 2)
        .map((m) => `${m.name} at ${m.current_score}`)

      const data = await api.generateSummary({
        team_risk_summary: `${highRisk} high, ${mediumRisk} medium, ${lowRisk} low risk`,
        top_concerns: topConcerns.length > 0
          ? topConcerns
          : [`${members[0].name} at ${members[0].current_score}`],
      })
      setSummary(data.summary)
    } catch (err) {
      console.error('Failed to generate summary:', err)
    } finally {
      setSummaryLoading(false)
    }
  }

  const getRiskLevel = (score) => {
    if (score < 40) return 'low'
    if (score < 70) return 'medium'
    return 'high'
  }

  const copyJoinCode = async () => {
    const code = team?.team?.join_code
    if (!code) return
    try {
      await navigator.clipboard.writeText(code)
      showToast('Join code copied', 'success')
    } catch {
      showToast(code, 'info')
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-6 bg-[#EDEAF1] rounded w-3/4 mb-4" />
              <div className="h-12 bg-[#EDEAF1] rounded" />
              <div className="h-4 bg-[#EDEAF1] rounded w-1/2 mt-4" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container text-center py-12">
        <p className="text-risk-high mb-4">Failed to load team: {error}</p>
        <Button onClick={refetch}>Retry</Button>
      </div>
    )
  }

  return (
    <div className="page-container">
      <ToastContainer />

      <AppHeader
        title={team?.team?.name || 'Team Workload'}
        subtitle={`Manager view for ${member?.name || 'your team'} — personal check-ins stay private`}
        extra={
          <Button variant="secondary" onClick={refetch} size="sm">
            Refresh
          </Button>
        }
      />

      {team?.team?.join_code && (
        <div className="card p-4 mb-6 flex flex-wrap items-center justify-between gap-3 bg-brand-primary/5 border-l-4 border-brand-primary">
          <div>
            <p className="text-sm text-text-muted">Share this join code with caregivers</p>
            <p className="font-mono text-lg font-semibold text-brand-primary tracking-widest">
              {team.team.join_code}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={copyJoinCode}>
            Copy code
          </Button>
        </div>
      )}

      {summary && (
        <div className="card p-4 mb-6 bg-brand-primary/5 border-l-4 border-brand-primary">
          <p className="text-text-primary text-sm">{summary}</p>
        </div>
      )}
      {summaryLoading && (
        <div className="card p-4 mb-6 animate-pulse">
          <div className="h-4 bg-brand-primary/20 rounded w-3/4" />
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {members.map((m) => (
          <Link key={m.id} to={`/manager/member/${m.id}`} className="block">
            <div className="card p-5 hover:shadow-card-hover transition-shadow duration-200 group">
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <Avatar initials={m.avatar_initials} size="lg" />
                  <div>
                    <h3 className="font-semibold text-text-primary group-hover:text-brand-primary transition-colors">
                      {m.name}
                    </h3>
                    <Badge variant={getRiskLevel(m.current_score)} className="text-xs">
                      {getRiskLevel(m.current_score)} risk
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="flex items-end justify-between gap-4">
                <RiskScoreDisplay score={m.current_score} size="md" showLabel={false} />
                <div className="flex-1 min-w-0">
                  <Sparkline data={m.score_trend} height={50} />
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-[#EDEAF1]">
                <p className="text-xs text-text-muted">
                  {m.top_drivers?.length
                    ? m.top_drivers.slice(0, 2).join(' · ')
                    : m.score_trend?.length
                      ? `${m.score_trend.length} days of history`
                      : 'No workload history yet'}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {members.length === 0 && (
        <div className="text-center py-12 text-text-muted">
          No caregivers on this team yet. Share the join code so members can sign up and connect.
        </div>
      )}
    </div>
  )
}
