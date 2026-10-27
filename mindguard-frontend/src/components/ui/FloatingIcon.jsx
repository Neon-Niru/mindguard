export default function FloatingIcon({ icon: Icon, className = '', tone = 'bg-brand-gradient', delay = '0s' }) {
  return (
    <div
      className={`absolute rounded-2xl flex items-center justify-center shadow-glow animate-float ${tone} ${className}`}
      style={{ animationDelay: delay }}
    >
      <Icon className="text-white" />
    </div>
  )
}
