import { Badge } from './Badge'
import { Button } from './Button'
import { Avatar } from './Avatar'

export function ReassignmentProposal({ proposal, onAccept, onDismiss, loading }) {
  if (!proposal) return null
  
  const fromMember = proposal.from_member
  const toMember = proposal.to_member
  const task = proposal.tasks
  
  return (
    <div className="card p-4 border-l-4 border-brand-accent bg-brand-accent/5">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1">
          <p className="font-medium text-text-primary mb-1">
            Suggested task reassignment
          </p>
          <p className="text-sm text-text-muted">{proposal.reason}</p>
        </div>
        <Badge variant="medium">Pending</Badge>
      </div>
      
      <div className="flex items-center gap-4 mb-4 p-3 bg-surface rounded-lg">
        <div className="flex items-center gap-3">
          <Avatar initials={fromMember?.avatar_initials || '?'} size="sm" />
          <div>
            <p className="font-medium text-text-primary text-sm">{fromMember?.name || 'Current assignee'}</p>
            <p className="text-xs text-text-muted">Current assignee</p>
          </div>
        </div>
        
        <svg className="mx-2 text-text-muted" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
        
        <div className="flex items-center gap-3">
          <Avatar initials={toMember?.avatar_initials || '?'} size="sm" />
          <div>
            <p className="font-medium text-text-primary text-sm">{toMember?.name || 'Suggested assignee'}</p>
            <p className="text-xs text-text-muted">Suggested assignee</p>
          </div>
        </div>
      </div>
      
      {task && (
        <div className="mb-4 p-3 bg-surface rounded-lg">
          <p className="text-xs text-text-muted mb-1">Task to reassign</p>
          <p className="font-medium text-text-primary">{task.title}</p>
          <div className="flex items-center gap-2 mt-1">
            <Badge 
              variant={task.priority === 'high' ? 'high' : task.priority === 'medium' ? 'medium' : 'low'}
              className="text-xs"
            >
              {task.priority} priority
            </Badge>
            <span className="text-xs text-text-muted">{task.estimated_hours}h</span>
          </div>
        </div>
      )}
      
      <div className="flex items-center justify-end gap-3">
        <Button 
          variant="ghost" 
          onClick={() => onDismiss(proposal.id)}
          disabled={loading}
        >
          Dismiss
        </Button>
        <Button 
          variant="primary" 
          onClick={() => onAccept(proposal.id)}
          disabled={loading}
        >
          Accept reassignment
        </Button>
      </div>
    </div>
  )
}