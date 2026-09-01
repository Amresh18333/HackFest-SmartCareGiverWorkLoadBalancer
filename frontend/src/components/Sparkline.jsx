import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const RISK_COLORS = {
  low: '#7FA98D',
  medium: '#E8A94C',
  high: '#D2685F',
}

export function Sparkline({ data, height = 60, showTooltip = false }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full" style={{ height }}>
        <div className="h-full flex items-center justify-center text-text-muted text-xs">
          No data
        </div>
      </div>
    )
  }
  
  // Determine color based on latest score
  const latestScore = data[data.length - 1]?.score || 0
  const color = latestScore < 40 ? RISK_COLORS.low : latestScore < 70 ? RISK_COLORS.medium : RISK_COLORS.high
  
  return (
    <div style={{ height, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EDEAF1" vertical={false} />
          <XAxis 
            dataKey="date" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontSize: 9, fill: '#8B8494' }}
            interval="preserveStartEnd"
            tickFormatter={(value) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
          />
          <YAxis 
            domain={[0, 100]} 
            axisLine={false} 
            tickLine={false} 
            tick={false}
            min={0}
            max={100}
          />
          <Tooltip 
            content={({ active, payload }) => {
              if (!showTooltip || !active) return null
              const item = payload[0]?.payload
              if (!item) return null
              return (
                <div className="bg-surface border border-[#D4D0DB] rounded-lg p-2 shadow-card">
                  <p className="font-medium text-text-primary">{new Date(item.date).toLocaleDateString()}</p>
                  <p className="text-sm text-text-muted">Risk score: <span className="font-medium text-text-primary">{item.score}</span></p>
                </div>
              )
            }}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: color }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}