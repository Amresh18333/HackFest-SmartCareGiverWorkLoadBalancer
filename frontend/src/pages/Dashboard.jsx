import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMembers } from '../hooks/useMembers'
import { Sparkline } from '../components/Sparkline'
import { RiskScoreDisplay } from '../components/RiskScoreDisplay'
import { Avatar } from '../components/Avatar'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { ToastContainer } from '../components/Toast'

export function Dashboard() {
  const { members, loading, error, refetch } = useMembers()
  const [summary, setSummary] = useState('')
  const [summaryLoading, setSummaryLoading] = useState(false)
  
  // Generate LLM summary when members load
  useEffect(() => {
    if (members.length > 0 && !summary) {
      generateSummary()
    }
  }, [members])
  
  const generateSummary = async () => {
    setSummaryLoading(true)
    try {
      const highRisk = members.filter(m => m.current_score >= 70).length
      const mediumRisk = members.filter(m => m.current_score >= 40 && m.current_score < 70).length
      const lowRisk = members.filter(m => m.current_score < 40).length
      
      const topConcerns = members
        .filter(m => m.current_score >= 70)
        .sort((a, b) => b.current_score - a.current_score)
        .slice(0, 2)
        .map(m => `${m.name} at ${m.current_score}`)
      
      const response = await fetch('/api/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_risk_summary: `${highRisk} high, ${mediumRisk} medium, ${lowRisk} low risk`,
          top_concerns: topConcerns.length > 0 ? topConcerns : [`${members[0].name} at ${members[0].current_score}`]
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setSummary(data.summary)
      }
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
  
  if (loading) {
    return (
      <div className="page-container">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[1,2,3,4,5].map(i => (
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
      
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Team Workload</h1>
            <p className="text-text-muted mt-1">Burnout risk overview — updated live</p>
          </div>
          <Button variant="secondary" onClick={refetch} size="sm">
            Refresh
          </Button>
        </div>
        
        {/* AI Summary */}
        {summary && (
          <div className="card p-4 bg-brand-primary/5 border-l-4 border-brand-primary">
            <p className="text-text-primary text-sm">{summary}</p>
          </div>
        )}
        {summaryLoading && (
          <div className="card p-4 animate-pulse">
            <div className="h-4 bg-brand-primary/20 rounded w-3/4" />
          </div>
        )}
      </header>
      
      {/* Team Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {members.map((member) => (
          <Link key={member.id} to={`/member/${member.id}`} className="block">
            <div className="card p-5 hover:shadow-card-hover transition-shadow duration-200 group">
              {/* Header with avatar and name */}
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <Avatar initials={member.avatar_initials} size="lg" />
                  <div>
                    <h3 className="font-semibold text-text-primary group-hover:text-brand-primary transition-colors">
                      {member.name}
                    </h3>
                    <Badge variant={getRiskLevel(member.current_score)} className="text-xs">
                      {getRiskLevel(member.current_score)} risk
                    </Badge>
                  </div>
                </div>
              </div>
              
              {/* Risk Score & Sparkline */}
              <div className="flex items-end justify-between gap-4">
                <RiskScoreDisplay score={member.current_score} size="md" showLabel={false} />
                <div className="flex-1 min-w-0">
                  <Sparkline data={member.score_trend} height={50} />
                </div>
              </div>
              
              {/* Drivers hint */}
              <div className="mt-3 pt-3 border-t border-[#EDEAF1]">
                <p className="text-xs text-text-muted">
                  {member.score_trend.length > 0 
                    ? `${member.score_trend.length} days of history`
                    : 'No history yet'}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>
      
      {members.length === 0 && (
        <div className="text-center py-12 text-text-muted">
          No team members found. Add members in Supabase to get started.
        </div>
      )}
    </div>
  )
}