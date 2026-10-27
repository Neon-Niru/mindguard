export default function Button({ children, variant = 'primary', className = '', icon: Icon, type = 'button', ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-full font-medium transition-all duration-300 px-6 py-3 text-sm'
  const variants = {
    primary: 'bg-brand-gradient text-white shadow-glow-sm hover:shadow-glow hover:brightness-110 active:scale-[0.98]',
    secondary: 'glass text-text-hi hover:bg-glass-fillhover active:scale-[0.98]',
    ghost: 'text-text-lo hover:text-text-hi hover:bg-white/5',
  }
  return (
    <button type={type} className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
      {Icon && <Icon size={16} />}
    </button>
  )
}
