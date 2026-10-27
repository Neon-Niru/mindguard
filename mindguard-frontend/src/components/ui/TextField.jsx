export default function TextField({ label, type = 'text', placeholder, icon: Icon, className = '', ...props }) {
  return (
    <label className={`block ${className}`}>
      <span className="block text-xs text-text-lo mb-2">{label}</span>
      <div className="relative">
        {Icon && <Icon size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-text-faint" />}
        <input
          type={type}
          placeholder={placeholder}
          className={`w-full bg-white/5 border border-white/10 rounded-xl py-3 ${Icon ? 'pl-11' : 'pl-4'} pr-4 text-sm text-text-hi placeholder:text-text-faint outline-none focus:border-accent-purple/50 focus:bg-white/[0.07] transition-colors`}
          {...props}
        />
      </div>
    </label>
  )
}
