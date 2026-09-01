import { Badge } from './Badge'

export function RiskScoreDisplay({ score, size = 'md', showLabel = true }) {
  const getRiskLevel = (s) => {
    if (s < 40) return 'low'
    if (s < 70) return 'medium'
    return 'high'
  }
  
  const riskLevel = getRiskLevel(score)
  const riskColors = {
    low: 'risk-low',
    medium: 'risk-medium',
    high: 'risk-high',
  }
  
  const sizes = {
    sm: 'text-2xl',
    md: 'text-4xl',
    lg: 'text-6xl',
  }
  
  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`${riskColors[riskLevel]} font-bold ${sizes[size]}`}>
        {score}
      </div>
      {showLabel && (
        <Badge variant={riskLevel} className="text-xs">
          {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} risk
        </Badge>
      )}
    </div>
  )
}