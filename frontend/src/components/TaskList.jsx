import { Badge } from './Badge'
import { Button } from './Button'

const PRIORITY_COLORS = {
  high: 'bg-risk-high/15 text-risk-high border-risk-high/30',
  medium: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
  low: 'bg-risk-low/15 text-risk-low border-risk-low/30',
}

const STATUS_COLORS = {
  todo: 'bg-[#EDEAF1] text-text-muted',
  in_progress: 'bg-brand-primary/15 text-brand-primary',
  done: 'bg-risk-low/15 text-risk-low',
}

const STATUS_ORDER = { todo: 0, in_progress: 1, done: 2 }

export function TaskList({ tasks, onReassign, onStatusChange, showAssignee = false }) {
  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted">
        No tasks assigned
      </div>
    )
  }
  
  // Sort by status order, then priority
  const sortedTasks = [...tasks].sort((a, b) => {
    const statusDiff = STATUS_ORDER[a.status] - STATUS_ORDER[b.status]
    if (statusDiff !== 0) return statusDiff
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    return priorityOrder[a.priority] - priorityOrder[b.priority]
  })
  
  return (
    <div className="space-y-3">
      {sortedTasks.map((task) => (
        <div 
          key={task.id} 
          className="card p-4 flex items-center justify-between gap-4"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-medium text-text-primary truncate">{task.title}</h4>
              <Badge 
                className={PRIORITY_COLORS[task.priority] || 'badge'}
              >
                {task.priority}
              </Badge>
              <Badge 
                className={STATUS_COLORS[task.status] || 'badge'}
              >
                {task.status.replace('_', ' ')}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-text-muted">
              <span>{task.estimated_hours}h</span>
              {task.due_date && (
                <span>Due {new Date(task.due_date).toLocaleDateString()}</span>
              )}
              {showAssignee && task.assignee && (
                <span>→ {task.assignee.name}</span>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {onStatusChange && (
              <select
                value={task.status}
                onChange={(e) => onStatusChange(task, e.target.value)}
                className="px-2 py-1 text-sm border border-[#D4D0DB] rounded-lg bg-surface focus:outline-none focus:ring-2 focus:ring-brand-primary"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
            )}
            
            {onReassign && task.status !== 'done' && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onReassign(task)}
              >
                Reassign
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}