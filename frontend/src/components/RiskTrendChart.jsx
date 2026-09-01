import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Legend, ReferenceLine 
} from 'recharts'

const RISK_COLORS = {
  low: '#7FA98D',
  medium: '#E8A94C',
  high: '#D2685F',
}

const RISK_ZONES = [
  { min: 0, max: 39, color: '#7FA98D', opacity: 0.08, label: 'Low' },
  { min: 40, max: 69, color: '#E8A94C', opacity: 0.08, label: 'Medium' },
  { min: 70, max: 100, color: '#D2685F', opacity: 0.08, label: 'High' },
]

export function RiskTrendChart({ data, height = 300 }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-text-muted" style={{ height }}>
        No risk history available
      </div>
    )
  }
  
  const latestScore = data[data.length - 1]?.score || 0
  const lineColor = latestScore < 40 ? RISK_COLORS.low : latestScore < 70 ? RISK_COLORS.medium : RISK_COLORS.high
  
  return (
    <div style={{ height, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          {/* Risk zone backgrounds */}
          {RISK_ZONES.map((zone, i) => (
            <ReferenceLine
              key={i}
              type="segment"
              y={zone.min}
              y2={zone.max}
              stroke={zone.color}
              strokeWidth={0}
              fill={zone.color}
              fillOpacity={zone.opacity}
            />
          ))}
          
          <CartesianGrid strokeDasharray="3 3" stroke="#EDEAF1" vertical={false} />
          
          <XAxis 
            dataKey="date" 
            axisLine={{ stroke: '#D4D0DB' }} 
            tickLine={false}
            tick={{ fontSize: 11, fill: '#8B8494' }}
            interval="preserveStartEnd"
            tickFormatter={(value) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
          />
          
          <YAxis 
            domain={[0, 100]} 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontSize: 11, fill: '#8B8494' }}
            min={0}
            max={100}
            tickFormatter={(value) => `${value}`}
          />
          
          <Tooltip 
            content={({ active, payload }) => {
              if (!active) return null
              const item = payload[0]?.payload
              if (!item) return null
              const level = item.score < 40 ? 'Low' : item.score < 70 ? 'Medium' : 'High'
              const levelColor = item.score < 40 ? RISK_COLORS.low : item.score < 70 ? RISK_COLORS.medium : RISK_COLORS.high
              return (
                <div className="bg-surface border border-[#D4D0DB] rounded-lg p-3 shadow-card min-w-[180px]">
                  <p className="font-medium text-text-primary mb-1">
                    {new Date(item.date).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className={`font-bold text-xl`} style={{ color: levelColor }}>
                      {item.score}
                    </span>
                    <span className="badge" style={{ backgroundColor: `${levelColor}20`, color: levelColor }}>
                      {level} risk
                    </span>
                  </div>
                </div>
              )
            }}
          />
          
          <Legend />
          
          <Line
            name="Risk Score"
            type="monotone"
            dataKey="score"
            stroke={lineColor}
            strokeWidth={3}
            dot={{ r: 4, fill: lineColor, stroke: '#FFFFFF', strokeWidth: 2 }}
            activeDot={{ r: 6, fill: lineColor, stroke: '#FFFFFF', strokeWidth: 2 }}
            animationDuration={500}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Risk zone legend */}
      <div className="flex items-center justify-center gap-4 mt-3 text-xs text-text-muted">
        {RISK_ZONES.map((zone, i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded" style={{ backgroundColor: zone.color, opacity: 0.3 }} />
            {zone.label} ({zone.min}-{zone.max})
          </span>
        ))}
      </div>
    </div>
  )
}