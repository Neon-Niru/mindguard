import { useState, useEffect } from 'react'
import { User, Lock, Bell, Palette, Bot, ShieldCheck, LogOut, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/ui/PageHeader.jsx'
import GlassCard from '../components/ui/GlassCard.jsx'
import Button from '../components/ui/Button.jsx'
import TextField from '../components/ui/TextField.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { settings as settingsApi } from '../services/api'

function Toggle({ checked, onChange }) {
  return (
    <button
      onClick={onChange}
      className={`w-11 h-6 rounded-full relative transition-colors shrink-0 ${checked ? 'bg-brand-gradient' : 'bg-white/10'}`}
      aria-pressed={checked}
    >
      <span
        className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${checked ? 'translate-x-[22px]' : 'translate-x-0.5'}`}
      />
    </button>
  )
}

function Row({ label, description, right }) {
  return (
    <div className="flex items-center justify-between gap-4 py-4">
      <div>
        <p className="text-sm text-text-hi">{label}</p>
        {description && <p className="text-xs text-text-faint mt-0.5">{description}</p>}
      </div>
      {right}
    </div>
  )
}

const sections = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'password', label: 'Password', icon: Lock },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'theme', label: 'Theme', icon: Palette },
  { id: 'ai', label: 'AI Configuration', icon: Bot },
  { id: 'privacy', label: 'Privacy', icon: ShieldCheck },
]

export default function Settings() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [active, setActive] = useState('profile')
  const [notifs, setNotifs] = useState({ checkins: true, planner: true, weekly: false })
  const [darkMode, setDarkMode] = useState(true)
  const [aiTone, setAiTone] = useState('supportive')
  const [dataSharing, setDataSharing] = useState(false)

  useEffect(() => {
    settingsApi.get()
      .then((data) => {
        setDarkMode(data.theme === 'dark')
        setNotifs({ checkins: data.notifications, planner: data.notifications, weekly: false })
        setDataSharing(data.privacy_settings !== 'private')
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    settingsApi.save({
      theme: darkMode ? 'dark' : 'light',
      notifications: notifs.checkins || notifs.planner,
      privacy_settings: dataSharing ? 'shared' : 'private',
    }).catch(() => {})
  }, [notifs, darkMode, dataSharing])

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div>
      <PageHeader eyebrow="Settings" title="Account Settings" description="Manage your profile, preferences, and privacy." />

      <div className="grid lg:grid-cols-[220px_1fr] gap-6">
        <GlassCard className="p-3 h-fit lg:sticky lg:top-8">
          <nav className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-visible">
            {sections.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActive(id)}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm whitespace-nowrap transition-colors ${
                  active === id ? 'bg-brand-gradient text-white' : 'text-text-lo hover:text-text-hi hover:bg-white/5'
                }`}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm text-rose-300/80 hover:text-rose-300 hover:bg-white/5 transition-colors mt-1 lg:mt-2 lg:border-t lg:border-white/10 lg:pt-3.5"
            >
              <LogOut size={16} />
              Log Out
            </button>
          </nav>
        </GlassCard>

        <GlassCard className="p-7">
          {active === 'profile' && (
            <div>
              <h3 className="font-medium mb-5">Profile</h3>
              <div className="flex items-center gap-4 mb-7">
                <div className="w-16 h-16 rounded-full bg-brand-gradient flex items-center justify-center text-xl font-semibold">
                  {(user?.full_name || 'U')[0]}
                </div>
                <Button variant="secondary">Change Photo</Button>
              </div>
              <div className="grid sm:grid-cols-2 gap-5 max-w-xl">
                <TextField label="Full name" defaultValue={user?.full_name || ''} />
                <TextField label="Email" type="email" defaultValue={user?.email || ''} className="sm:col-span-2" />
              </div>
            </div>
          )}

          {active === 'password' && (
            <div>
              <h3 className="font-medium mb-5">Password</h3>
              <div className="space-y-5 max-w-md">
                <TextField label="Current password" type="password" placeholder="••••••••" />
                <TextField label="New password" type="password" placeholder="At least 6 characters" />
                <TextField label="Confirm new password" type="password" placeholder="••••••••" />
              </div>
              <Button variant="primary" className="mt-7">Update Password</Button>
            </div>
          )}

          {active === 'notifications' && (
            <div>
              <h3 className="font-medium mb-2">Notifications</h3>
              <div className="divide-y divide-white/10">
                <Row label="Check-in reminders" description="Gentle nudges to check in with your AI companion" right={<Toggle checked={notifs.checkins} onChange={() => setNotifs((n) => ({ ...n, checkins: !n.checkins }))} />} />
                <Row label="Planner reminders" description="Alerts for upcoming planner tasks" right={<Toggle checked={notifs.planner} onChange={() => setNotifs((n) => ({ ...n, planner: !n.planner }))} />} />
                <Row label="Weekly summary" description="A recap of your wellness trends each week" right={<Toggle checked={notifs.weekly} onChange={() => setNotifs((n) => ({ ...n, weekly: !n.weekly }))} />} />
              </div>
            </div>
          )}

          {active === 'theme' && (
            <div>
              <h3 className="font-medium mb-2">Theme</h3>
              <Row label="Dark mode" description="MindGuard AI is designed for a calming dark interface" right={<Toggle checked={darkMode} onChange={() => setDarkMode((d) => !d)} />} />
            </div>
          )}

          {active === 'ai' && (
            <div>
              <h3 className="font-medium mb-5">AI Configuration</h3>
              <p className="text-xs text-text-lo mb-3">Conversation tone</p>
              <div className="grid sm:grid-cols-3 gap-3">
                {['supportive', 'direct', 'reflective'].map((tone) => (
                  <button
                    key={tone}
                    onClick={() => setAiTone(tone)}
                    className={`px-4 py-3 rounded-xl text-sm capitalize border transition-colors ${
                      aiTone === tone ? 'bg-brand-gradient border-transparent text-white' : 'border-white/10 text-text-lo hover:text-text-hi'
                    }`}
                  >
                    {tone}
                  </button>
                ))}
              </div>
            </div>
          )}

          {active === 'privacy' && (
            <div>
              <h3 className="font-medium mb-2">Privacy</h3>
              <div className="divide-y divide-white/10">
                <Row label="Share anonymized data for research" description="Helps improve the burnout detection model" right={<Toggle checked={dataSharing} onChange={() => setDataSharing((d) => !d)} />} />
                <Row label="Download my data" right={<button className="text-xs text-accent-purple hover:text-accent-teal flex items-center gap-1">Request <ChevronRight size={13} /></button>} />
                <Row label="Delete my account" description="Permanently remove your account and data" right={<button className="text-xs text-rose-300 hover:text-rose-200">Delete</button>} />
              </div>
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  )
}
