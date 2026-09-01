export function Avatar({ initials, size = 'md', className = '' }) {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  }
  
  return (
    <div 
      className={`avatar ${sizes[size]} ${className}`}
      aria-label={initials}
    >
      {initials}
    </div>
  )
}