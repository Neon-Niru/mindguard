const tones = {
  low: 'text-accent-teal bg-accent-teal/10 border-accent-teal/25',
  moderate: 'text-accent-amber bg-accent-amber/10 border-accent-amber/25',
  high: 'text-rose-300 bg-rose-400/10 border-rose-400/25',
  neutral: 'text-text-lo bg-white/5 border-white/10',
  brand: 'text-accent-purple bg-accent-purple/10 border-accent-purple/25',
}

export default function Badge({ children, tone = 'neutral', className = '' }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${tones[tone]} ${className}`}>
      {children}
    </span>
  )
}
