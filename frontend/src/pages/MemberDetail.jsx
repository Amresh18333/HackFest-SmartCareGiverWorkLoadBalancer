import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useMember } from '../hooks/useMembers'
import { api } from '../lib/api'
import { RiskTrendChart } from '../components/RiskTrendChart'
import { RiskScoreDisplay } from '../components/RiskScoreDisplay'
import { TaskList } from '../components/TaskList'
import { ReassignmentProposal } from '../components/ReassignmentProposal'
import { Avatar } from '../components/Avatar'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { ToastContainer, showToast } from '../components/Toast'

export function MemberDetail() {
  const { memberId } = useParams()
  const { member, loading, error, refetch } = useMember(memberId)
  const [activeTab, setActiveTab] = useState('overview')
  const [proposalLoading, setProposalLoading] = useState(null)
  
  const getRiskLevel = (score) => {
    if (score < 40) return 'low'
    if (score < 70) return 'medium'
    return 'high'
  }
  
  const handleAccept = async (proposalId) => {
    setProposalLoading(proposalId)
    try {
      await api.resolveReassignment(proposalId, 'accepted')
      showToast('Task reassigned successfully', 'success')
      refetch()
    } catch (err) {
      showToast(err.message || 'Failed to accept reassignment', 'error')
    } finally {
      setProposalLoading(null)
    }
  }
  
  const handleDismiss = async (proposalId) => {
    setProposalLoading(proposalId)
    try {
      await api.resolveReassignment(proposalId, 'dismissed')
      showToast('Proposal dismissed', 'info')
      refetch()
    } catch (err) {
      showToast(err.message || 'Failed to dismiss proposal', 'error')
    } finally {
      setProposalLoading(null)
    }
  }
  
  const handleRecompute = async () => {
    try {
      await api.recomputeRisk(memberId)
      showToast('Risk score updated', 'success')
      refetch()
    } catch (err) {
      showToast(err.message || 'Failed to recompute risk', 'error')
    }
  }
  
  if (loading) {
    return (
      <div className="page-container">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-[#EDEAF1] rounded w-1/4" />
          <div className="h-64 bg-[#EDEAF1] rounded" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64 bg-[#EDEAF1] rounded" />
            <div className="h-64 bg-[#EDEAF1] rounded" />
          </div>
        </div>
      </div>
    )
  }
  
  if (error || !member) {
    return (
      <div className="page-container text-center py-12">
        <p className="text-risk-high mb-4">Failed to load member: {error || 'Not found'}</p>
        <Link to="/manager" className="btn-outline inline-block">← Back to team</Link>
      </div>
    )
  }
  
  const riskLevel = getRiskLevel(member.current_score)
  const incompleteTasks = member.tasks?.filter(t => t.status !== 'done') || []
  const pendingProposals = member.pending_reassignments?.filter(p => p.status === 'pending') || []
  
  return (
    <div className="page-container">
      <ToastContainer />
      
      {/* Header */}
      <header className="mb-8">
        <Link to="/manager" className="btn-ghost mb-4 inline-flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to team
        </Link>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Avatar initials={member.avatar_initials} size="xl" />
            <div>
              <h1 className="text-3xl font-bold text-text-primary">{member.name}</h1>
              <p className="text-text-muted">{member.timezone}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <RiskScoreDisplay score={member.current_score} size="md" showLabel={true} />
            <Button variant="outline" onClick={handleRecompute} size="sm">
              Refresh score
            </Button>
          </div>
        </div>
      </header>
      
      {/* Tab Navigation */}
      <nav className="flex gap-1 mb-6 bg-surface rounded-card p-1 shadow-card" role="tablist">
        {[
          { id: 'overview', label: 'Overview', icon: '📊' },
          { id: 'tasks', label: 'Tasks', icon: '📋' },
          { id: 'proposals', label: 'Proposals', icon: '🔄', count: pendingProposals.length },
        ].map(tab => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-brand-primary text-white shadow-card'
                : 'text-text-muted hover:text-text-primary hover:bg-[#EDEAF1]'
            }`}
          >
            <span className="flex items-center gap-2">
              {tab.icon} {tab.label}
              {tab.count && (
                <span className="badge bg-brand-primary/20 text-brand-primary ml-1">
                  {tab.count}
                </span>
              )}
            </span>
          </button>
        ))}
      </nav>
      
      {/* Tab Panels */}
      <div role="tabpanel" id={activeTab}>
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Trend Chart */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-text-primary">Risk Trend (30 days)</h2>
                <Badge variant={riskLevel}>{riskLevel} risk</Badge>
              </div>
              <RiskTrendChart data={member.score_history} height={280} />
            </div>
            
            {/* Key Drivers */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4">Key Drivers</h2>
              {member.top_drivers && member.top_drivers.length > 0 ? (
                <div className="space-y-3">
                  {member.top_drivers.map((driver, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 bg-[#F7F5FA] rounded-lg">
                      <div className="w-2 h-2 rounded-full" style={{ 
                        backgroundColor: riskLevel === 'high' ? '#D2685F' : riskLevel === 'medium' ? '#E8A94C' : '#7FA98D' 
                      }} />
                      <span className="text-text-primary">{driver}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-text-muted">No driver data available</p>
              )}
              
              <div className="mt-6 pt-4 border-t border-[#EDEAF1]">
                <h3 className="text-sm font-medium text-text-primary mb-3">Workload signals</h3>
                <p className="text-xs text-text-muted mb-3">
                  Personal check-ins, late-night activity, and response times stay private to the caregiver.
                </p>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {member.tasks && (
                    <>
                      <div>
                        <p className="text-text-muted">Active tasks</p>
                        <p className="font-medium text-text-primary">{incompleteTasks.length}</p>
                      </div>
                      <div>
                        <p className="text-text-muted">Total hours</p>
                        <p className="font-medium text-text-primary">
                          {incompleteTasks.reduce((sum, t) => sum + (t.estimated_hours || 0), 0).toFixed(1)}h
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'tasks' && (
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Assigned Tasks</h2>
              <Badge variant={incompleteTasks.length > 5 ? 'high' : incompleteTasks.length > 2 ? 'medium' : 'low'}>
                {incompleteTasks.length} active
              </Badge>
            </div>
            <TaskList 
              tasks={member.tasks} 
              showAssignee={false}
            />
          </div>
        )}
        
        {activeTab === 'proposals' && (
          <div className="space-y-4">
            {pendingProposals.length > 0 ? (
              pendingProposals.map(proposal => (
                <ReassignmentProposal
                  key={proposal.id}
                  proposal={proposal}
                  onAccept={handleAccept}
                  onDismiss={handleDismiss}
                  loading={proposalLoading === proposal.id}
                />
              ))
            ) : (
              <div className="card p-8 text-center">
                <svg className="mx-auto mb-4 text-text-muted" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                <h3 className="text-lg font-medium text-text-primary mb-1">No pending proposals</h3>
                <p className="text-text-muted">Rebalancing suggestions will appear here when risk crosses threshold</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}