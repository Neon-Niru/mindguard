import { Link } from 'react-router-dom'
import { Brain, ShieldCheck } from 'lucide-react'

export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-16 relative overflow-hidden">
      <div className="absolute top-24 left-[8%] w-16 h-16 rounded-2xl bg-brand-gradient opacity-20 blur-sm animate-floatSlow hidden md:block" />
      <div className="absolute bottom-24 right-[10%] w-20 h-20 rounded-2xl bg-accent-teal/20 blur-sm animate-float hidden md:block" style={{ animationDelay: '1.2s' }} />

      <div className="w-full max-w-md relative z-10 animate-fadeUp">
        <Link to="/" className="flex items-center justify-center gap-2.5 mb-8">
          <span className="w-10 h-10 rounded-xl bg-brand-gradient flex items-center justify-center">
            <Brain size={19} className="text-white" />
          </span>
          <span className="font-display font-semibold text-lg">MindGuard AI</span>
        </Link>

        <div className="glass rounded-3xl p-8 md:p-9 shadow-glow">
          <div className="text-center mb-8">
            <div className="w-11 h-11 rounded-xl bg-brand-gradient-soft border border-white/10 flex items-center justify-center mx-auto mb-4">
              <ShieldCheck size={20} className="text-accent-purple" />
            </div>
            <h1 className="text-xl font-semibold mb-1.5">{title}</h1>
            {subtitle && <p className="text-sm text-text-lo">{subtitle}</p>}
          </div>
          {children}
        </div>

        {footer && <p className="text-center text-sm text-text-lo mt-6">{footer}</p>}
      </div>
    </div>
  )
}
