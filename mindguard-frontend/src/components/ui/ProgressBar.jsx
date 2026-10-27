export default function ProgressBar({ value = 0, className = '', height = 'h-2.5', label }) {
  const clamped = Math.max(0, Math.min(100, value))
  return (
    <div className={className}>
      {label && (
        <div className="flex justify-between text-xs text-text-lo mb-2">
          <span>{label}</span>
          <span className="text-text-hi font-medium">{clamped}%</span>
        </div>
      )}
      <div className={`w-full ${height} rounded-full bg-white/5 overflow-hidden`}>
        <div
          className={`${height} rounded-full bg-brand-gradient transition-all duration-700 ease-out`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  )
}
