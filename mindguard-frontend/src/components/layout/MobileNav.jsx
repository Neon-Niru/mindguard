import { NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageCircle, ListChecks, TrendingUp, Settings as SettingsIcon } from 'lucide-react'

const items = [
  { to: '/app/dashboard', icon: LayoutDashboard },
  { to: '/app/chat', icon: MessageCircle },
  { to: '/app/planner', icon: ListChecks },
  { to: '/app/progress', icon: TrendingUp },
  { to: '/app/settings', icon: SettingsIcon },
]

export default function MobileNav() {
  return (
    <div className="md:hidden fixed bottom-4 inset-x-4 z-40">
      <div className="glass rounded-2xl flex items-center justify-between px-3 py-3">
        {items.map(({ to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `p-2.5 rounded-xl transition-colors ${isActive ? 'bg-brand-gradient text-white' : 'text-text-lo'}`
            }
          >
            <Icon size={19} />
          </NavLink>
        ))}
      </div>
    </div>
  )
}
