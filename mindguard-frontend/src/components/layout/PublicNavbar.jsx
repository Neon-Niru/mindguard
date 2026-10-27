import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Brain, Menu, X } from 'lucide-react'
import Button from '../ui/Button.jsx'

const links = [
  { to: '/#home', label: 'Home' },
  { to: '/#features', label: 'Features' },
  { to: '/#how-it-works', label: 'How It Works' },
  { to: '/#about', label: 'About' },
  { to: '/#contact', label: 'Contact' },
]

export default function PublicNavbar() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <header className="fixed top-0 inset-x-0 z-50">
      <div className="max-w-7xl mx-auto px-6 pt-5">
        <nav className="glass rounded-full px-5 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center">
              <Brain size={18} className="text-white" />
            </span>
            <span className="font-display font-semibold text-lg">MindGuard AI</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {links.map((l) => (
              <a key={l.label} href={l.to} className="text-sm text-text-lo hover:text-text-hi transition-colors">
                {l.label}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <button onClick={() => navigate('/login')} className="text-sm px-4 py-2.5 rounded-full text-text-hi hover:bg-white/5 transition-colors">
              Login
            </button>
            <Button variant="primary" className="!px-5 !py-2.5" onClick={() => navigate('/register')}>
              Get Started
            </Button>
          </div>

          <button className="md:hidden text-text-hi" onClick={() => setOpen(!open)} aria-label="Toggle menu">
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </nav>

        {open && (
          <div className="glass rounded-3xl mt-3 p-5 md:hidden animate-fadeUp">
            <div className="flex flex-col gap-4">
              {links.map((l) => (
                <a key={l.label} href={l.to} onClick={() => setOpen(false)} className="text-sm text-text-lo hover:text-text-hi">
                  {l.label}
                </a>
              ))}
              <div className="flex gap-3 pt-3 border-t border-white/10">
                <button onClick={() => navigate('/login')} className="flex-1 text-sm py-2.5 rounded-full glass">Login</button>
                <button onClick={() => navigate('/register')} className="flex-1 text-sm py-2.5 rounded-full bg-brand-gradient text-white">Get Started</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
