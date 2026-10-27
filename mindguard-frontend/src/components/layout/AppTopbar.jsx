import { Bell, Menu } from 'lucide-react'

export default function AppTopbar({ title, onMenuClick }) {
  return (
    <div className="md:hidden sticky top-0 z-40 p-4">
      <div className="glass rounded-2xl px-4 py-3 flex items-center justify-between">
        <button onClick={onMenuClick} className="text-text-hi" aria-label="Open menu">
          <Menu size={20} />
        </button>
        <p className="font-display font-medium text-sm">{title}</p>
        <button className="text-text-lo" aria-label="Notifications">
          <Bell size={18} />
        </button>
      </div>
    </div>
  )
}
