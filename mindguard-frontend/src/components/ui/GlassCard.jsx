export default function GlassCard({ children, className = '', hover = false, glow = false, ...rest }) {
  return (
    <div
      className={`glass rounded-xl2 ${hover ? 'transition-all duration-300 hover:bg-glass-fillhover hover:-translate-y-1' : ''} ${glow ? 'shadow-glow' : ''} ${className}`}
      {...rest}
    >
      {children}
    </div>
  )
}
