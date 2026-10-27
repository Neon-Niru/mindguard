export default function StatTile({ icon: Icon, label, value, sub, iconTone = 'text-accent-purple bg-accent-purple/10' }) {
  return (
    <div className="glass rounded-2xl p-5 transition-all duration-300 hover:bg-glass-fillhover hover:-translate-y-0.5">
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-4 ${iconTone}`}>
        <Icon size={18} />
      </div>
      <p className="text-xs text-text-lo mb-1">{label}</p>
      <p className="text-2xl font-display font-semibold text-text-hi">{value}</p>
      {sub && <p className="text-xs text-text-faint mt-1">{sub}</p>}
    </div>
  )
}
