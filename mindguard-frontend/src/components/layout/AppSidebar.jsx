import { NavLink, useNavigate } from 'react-router-dom'
import {
  Brain,
  LayoutDashboard,
  MessageCircle,
  ListChecks,
  TrendingUp,
  Settings as SettingsIcon,
  LogOut,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'

const items = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/chat', label: 'AI Chat', icon: MessageCircle },
  { to: '/app/planner', label: 'Planner', icon: ListChecks },
  { to: '/app/progress', label: 'Progress', icon: TrendingUp },
  { to: '/app/settings', label: 'Settings', icon: SettingsIcon },
]

export default function AppSidebar() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U'

  return (
    <aside className="hidden md:flex flex-col w-64 shrink-0 h-screen sticky top-0 p-5">
      <div className="glass rounded-2xl flex flex-col h-full p-4">
        <button onClick={() => navigate('/')} className="flex items-center gap-2.5 px-2 py-2 mb-6">
          <span className="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center">
            <Brain size={18} className="text-white" />
          </span>
          <span className="font-display font-semibold">MindGuard AI</span>
        </button>

        <nav className="flex flex-col gap-1.5 flex-1">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-brand-gradient text-white shadow-glow-sm'
                    : 'text-text-lo hover:text-text-hi hover:bg-white/5'
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 pt-4 mt-4">
          <div className="flex items-center gap-3 px-2 mb-3">
            <div className="w-9 h-9 rounded-full bg-brand-gradient flex items-center justify-center text-sm font-semibold">
              {initials}
            </div>
            <div className="min-w-0">
              <p className="text-sm text-text-hi truncate">{user?.full_name || 'Student'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm text-text-lo hover:text-text-hi hover:bg-white/5 w-full transition-colors"
          >
            <LogOut size={17} />
            Log Out
          </button>
        </div>
      </div>
    </aside>
  )
}
