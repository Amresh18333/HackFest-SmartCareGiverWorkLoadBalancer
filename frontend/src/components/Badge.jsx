export function Badge({ children, variant = 'default', className = '' }) {
  const variants = {
    default: 'badge',
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
    risk: (score) => {
      if (score < 40) return 'badge-low'
      if (score < 70) return 'badge-medium'
      return 'badge-high'
    },
  }
  
  const variantClass = typeof variants[variant] === 'function' 
    ? variants[variant](children) 
    : variants[variant] || variants.default
  
  return (
    <span className={`${variantClass} ${className}`}>
      {children}
    </span>
  )
}