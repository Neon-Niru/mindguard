import { NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageCircle, ListChecks, TrendingUp, Settings as SettingsIcon } from 'lucide-react'

const items = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/chat', label: 'AI Chat', icon: MessageCircle },
  { to: '/app/planner', label: 'Planner', icon: ListChecks },
  { to: '/app/progress', label: 'Progress', icon: TrendingUp },
  { to: '/app/settings', label: 'Settings', icon: SettingsIcon },
]

export default function MobileNav() {
  return (
    <div className="md:hidden fixed bottom-4 inset-x-4 z-40">
      <nav className="glass rounded-2xl flex items-center justify-between px-3 py-3" aria-label="Primary">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            aria-label={label}
            className={({ isActive }) =>
              `p-2.5 rounded-xl transition-colors ${isActive ? 'bg-brand-gradient text-white' : 'text-text-lo'}`
            }
          >
            <Icon size={19} />
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
