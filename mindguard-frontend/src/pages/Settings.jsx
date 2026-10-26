import { useState, useEffect, useRef } from 'react'
import {
  User,
  Lock,
  Bell,
  Palette,
  Bot,
  ShieldCheck,
  LogOut,
  Download,
  Trash2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/ui/PageHeader.jsx'
import GlassCard from '../components/ui/GlassCard.jsx'
import Button from '../components/ui/Button.jsx'
import TextField from '../components/ui/TextField.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { auth, settings as settingsApi } from '../services/api'

function Toggle({ checked, onChange, disabled = false }) {
  return (
    <button
      type="button"
      onClick={onChange}
      disabled={disabled}
      className={`w-11 h-6 rounded-full relative transition-colors shrink-0 disabled:opacity-50 ${
        checked ? 'bg-brand-gradient' : 'bg-white/10'
      }`}
      aria-pressed={checked}
    >
      <span
        className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
          checked ? 'translate-x-[22px]' : 'translate-x-0.5'
        }`}
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

function Status({ status }) {
  if (!status) return null

  const isError = status.type === 'error'
  return (
    <p
      className={`flex items-center gap-2 text-sm rounded-lg px-4 py-2 mt-4 ${
        isError ? 'text-rose-300 bg-rose-300/10' : 'text-accent-teal bg-accent-teal/10'
      }`}
    >
      {isError ? <AlertCircle size={15} /> : <CheckCircle2 size={15} />}
      {status.message}
    </p>
  )
}

const sections = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'password', label: 'Password', icon: Lock },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'theme', label: 'Appearance', icon: Palette },
  { id: 'ai', label: 'AI Configuration', icon: Bot },
  { id: 'privacy', label: 'Privacy & Data', icon: ShieldCheck },
]

const DEFAULT_PREFS = {
  theme: 'dark',
  notification_checkins: true,
  notification_planner: true,
  notification_weekly: false,
  ai_tone: 'supportive',
  privacy_settings: 'private',
}

export default function Settings() {
  const navigate = useNavigate()
  const { user, logout, refreshUser } = useAuth()

  const [active, setActive] = useState('profile')
  const [prefs, setPrefs] = useState(DEFAULT_PREFS)
  const [loaded, setLoaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const [prefsStatus, setPrefsStatus] = useState(null)

  const [profile, setProfile] = useState({ full_name: '', email: '' })
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileStatus, setProfileStatus] = useState(null)

  const [passwords, setPasswords] = useState({
    current: '',
    next: '',
    confirm: '',
  })
  const [passwordSaving, setPasswordSaving] = useState(false)
  const [passwordStatus, setPasswordStatus] = useState(null)

  const [exporting, setExporting] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deletePassword, setDeletePassword] = useState('')
  const [deleteError, setDeleteError] = useState('')
  const [deleting, setDeleting] = useState(false)

  const prefsRef = useRef(DEFAULT_PREFS)
  const saveTimer = useRef(null)

  useEffect(() => {
    settingsApi.get()
      .then((data) => {
        const merged = { ...DEFAULT_PREFS, ...data }
        prefsRef.current = merged
        setPrefs(merged)
      })
      .catch((err) => {
        setPrefsStatus({ type: 'error', message: err.message })
      })
      .finally(() => setLoaded(true))
  }, [])

  useEffect(() => {
    if (user) {
      setProfile({ full_name: user.full_name || '', email: user.email || '' })
    }
  }, [user])

  useEffect(() => () => clearTimeout(saveTimer.current), [])

  async function persistPrefs(next) {
    setSaving(true)
    setPrefsStatus(null)

    try {
      const response = await settingsApi.save(next)
      const saved = { ...next, ...(response.settings || {}) }
      prefsRef.current = saved
      setPrefs(saved)
      setPrefsStatus({ type: 'success', message: 'Preferences saved.' })
    } catch (err) {
      setPrefsStatus({ type: 'error', message: err.message })
    } finally {
      setSaving(false)
    }
  }

  function updatePrefs(patch) {
    const next = { ...prefsRef.current, ...patch }
    prefsRef.current = next
    setPrefs(next)

    // Debounce rapid toggles into one request so the last value always wins.
    clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => persistPrefs(next), 350)
  }

  async function saveProfile(e) {
    e.preventDefault()
    setProfileStatus(null)
    setProfileSaving(true)

    try {
      const response = await auth.updateProfile({
        full_name: profile.full_name.trim(),
        email: profile.email.trim(),
      })
      refreshUser(response.user)
      setProfileStatus({ type: 'success', message: 'Profile updated.' })
    } catch (err) {
      setProfileStatus({ type: 'error', message: err.message })
    } finally {
      setProfileSaving(false)
    }
  }

  async function savePassword(e) {
    e.preventDefault()
    setPasswordStatus(null)

    if (passwords.next !== passwords.confirm) {
      setPasswordStatus({ type: 'error', message: 'New passwords do not match.' })
      return
    }

    setPasswordSaving(true)

    try {
      await auth.changePassword(passwords.current, passwords.next)
      setPasswords({ current: '', next: '', confirm: '' })
      setPasswordStatus({ type: 'success', message: 'Password updated.' })
    } catch (err) {
      setPasswordStatus({ type: 'error', message: err.message })
    } finally {
      setPasswordSaving(false)
    }
  }

  async function downloadData() {
    setExporting(true)
    setPrefsStatus(null)

    try {
      const data = await auth.exportData()
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `mindguard-data-${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      setPrefsStatus({ type: 'success', message: 'Your data has been downloaded.' })
    } catch (err) {
      setPrefsStatus({ type: 'error', message: err.message })
    } finally {
      setExporting(false)
    }
  }

  async function deleteAccount(e) {
    e.preventDefault()
    setDeleteError('')
    setDeleting(true)

    try {
      await auth.deleteAccount(deletePassword)
      logout()
      navigate('/login', { replace: true })
    } catch (err) {
      setDeleteError(err.message)
    } finally {
      setDeleting(false)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const initial = (user?.full_name || 'U').trim().charAt(0).toUpperCase()

  return (
    <div>
      <PageHeader
        eyebrow="Settings"
        title="Account Settings"
        description="Manage your profile, preferences, and privacy."
      />

      <div className="grid lg:grid-cols-[220px_1fr] gap-6">
        <GlassCard className="p-3 h-fit lg:sticky lg:top-8">
          <nav className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-visible">
            {sections.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActive(id)}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm whitespace-nowrap transition-colors ${
                  active === id
                    ? 'bg-brand-gradient text-white'
                    : 'text-text-lo hover:text-text-hi hover:bg-white/5'
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
                <div className="w-16 h-16 rounded-full bg-brand-gradient flex items-center justify-center text-xl font-semibold text-white">
                  {initial}
                </div>
                <p className="text-xs text-text-faint max-w-xs">
                  Your avatar uses your initials. Uploading photos is not enabled
                  in this build.
                </p>
              </div>

              <form onSubmit={saveProfile} className="grid sm:grid-cols-2 gap-5 max-w-xl">
                <TextField
                  label="Full name"
                  value={profile.full_name}
                  onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                  required
                />
                <TextField
                  label="Email"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  className="sm:col-span-2"
                  required
                />
                <div className="sm:col-span-2">
                  <Button type="submit" variant="primary" disabled={profileSaving}>
                    {profileSaving ? 'Saving...' : 'Save Profile'}
                  </Button>
                </div>
              </form>

              <Status status={profileStatus} />
            </div>
          )}

          {active === 'password' && (
            <div>
              <h3 className="font-medium mb-5">Password</h3>
              <form onSubmit={savePassword} className="space-y-5 max-w-md">
                <TextField
                  label="Current password"
                  type="password"
                  placeholder="••••••••"
                  value={passwords.current}
                  onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                  required
                />
                <TextField
                  label="New password"
                  type="password"
                  placeholder="At least 6 characters"
                  value={passwords.next}
                  onChange={(e) => setPasswords({ ...passwords, next: e.target.value })}
                  minLength={6}
                  required
                />
                <TextField
                  label="Confirm new password"
                  type="password"
                  placeholder="••••••••"
                  value={passwords.confirm}
                  onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                  minLength={6}
                  required
                />
                <Button type="submit" variant="primary" disabled={passwordSaving}>
                  {passwordSaving ? 'Updating...' : 'Update Password'}
                </Button>
              </form>

              <Status status={passwordStatus} />
            </div>
          )}

          {active === 'notifications' && (
            <div>
              <h3 className="font-medium mb-2">Notifications</h3>
              {!loaded ? (
                <p className="text-sm text-text-lo py-4">Loading preferences...</p>
              ) : (
                <div className="divide-y divide-white/10">
                  <Row
                    label="Check-in reminders"
                    description="Gentle nudges to check in with your AI companion"
                    right={
                      <Toggle
                        checked={prefs.notification_checkins}
                        onChange={() => updatePrefs({ notification_checkins: !prefs.notification_checkins })}
                        disabled={saving}
                      />
                    }
                  />
                  <Row
                    label="Planner reminders"
                    description="Alerts for upcoming planner tasks"
                    right={
                      <Toggle
                        checked={prefs.notification_planner}
                        onChange={() => updatePrefs({ notification_planner: !prefs.notification_planner })}
                        disabled={saving}
                      />
                    }
                  />
                  <Row
                    label="Weekly summary"
                    description="A recap of your wellness trends each week"
                    right={
                      <Toggle
                        checked={prefs.notification_weekly}
                        onChange={() => updatePrefs({ notification_weekly: !prefs.notification_weekly })}
                        disabled={saving}
                      />
                    }
                  />
                </div>
              )}
              <p className="text-xs text-text-faint mt-4">
                Reminders are saved here, but email and push delivery are not
                enabled in this build.
              </p>
              <Status status={prefsStatus} />
            </div>
          )}

          {active === 'theme' && (
            <div>
              <h3 className="font-medium mb-2">Appearance</h3>
              <Row
                label="Dark interface"
                description="MindGuard is designed as a calming dark experience. A light theme is not available in this build."
                right={
                  <span className="text-xs text-accent-teal bg-accent-teal/10 border border-accent-teal/25 rounded-full px-3 py-1">
                    Active
                  </span>
                }
              />
            </div>
          )}

          {active === 'ai' && (
            <div>
              <h3 className="font-medium mb-5">AI Configuration</h3>
              <p className="text-xs text-text-lo mb-3">Conversation tone</p>
              {!loaded ? (
                <p className="text-sm text-text-lo py-4">Loading preferences...</p>
              ) : (
                <>
                  <div className="grid sm:grid-cols-3 gap-3">
                    {[
                      { id: 'supportive', label: 'Supportive', hint: 'Warm and validating' },
                      { id: 'direct', label: 'Direct', hint: 'Concise and practical' },
                      { id: 'reflective', label: 'Reflective', hint: 'Mirrors your words' },
                    ].map((tone) => (
                      <button
                        key={tone.id}
                        onClick={() => updatePrefs({ ai_tone: tone.id })}
                        disabled={saving}
                        className={`px-4 py-3 rounded-xl text-left border transition-colors disabled:opacity-60 ${
                          prefs.ai_tone === tone.id
                            ? 'bg-brand-gradient border-transparent text-white'
                            : 'border-white/10 text-text-lo hover:text-text-hi'
                        }`}
                      >
                        <span className="block text-sm font-medium">{tone.label}</span>
                        <span className={`block text-xs mt-0.5 ${prefs.ai_tone === tone.id ? 'text-white/70' : 'text-text-faint'}`}>
                          {tone.hint}
                        </span>
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-text-faint mt-4">
                    This tone is applied to your next check-in conversation.
                  </p>
                </>
              )}
              <Status status={prefsStatus} />
            </div>
          )}

          {active === 'privacy' && (
            <div>
              <h3 className="font-medium mb-2">Privacy & Data</h3>
              {!loaded ? (
                <p className="text-sm text-text-lo py-4">Loading preferences...</p>
              ) : (
                <div className="divide-y divide-white/10">
                  <Row
                    label="Share anonymized data for research"
                    description="Helps improve the burnout model. Off by default."
                    right={
                      <Toggle
                        checked={prefs.privacy_settings === 'shared'}
                        onChange={() =>
                          updatePrefs({
                            privacy_settings:
                              prefs.privacy_settings === 'shared' ? 'private' : 'shared',
                          })
                        }
                        disabled={saving}
                      />
                    }
                  />
                  <Row
                    label="Download my data"
                    description="Export your profile, assessments, goals and tasks as JSON"
                    right={
                      <Button
                        variant="secondary"
                        icon={Download}
                        className="!px-4 !py-2 text-xs"
                        onClick={downloadData}
                        disabled={exporting}
                      >
                        {exporting ? 'Preparing...' : 'Download'}
                      </Button>
                    }
                  />
                  <Row
                    label="Delete my account"
                    description="Permanently remove your account and all wellness data"
                    right={
                      <Button
                        variant="secondary"
                        icon={Trash2}
                        className="!px-4 !py-2 text-xs !text-rose-300 hover:!bg-rose-300/10"
                        onClick={() => setDeleteOpen((open) => !open)}
                      >
                        Delete
                      </Button>
                    }
                  />
                </div>
              )}

              <p className="text-xs text-text-faint mt-4">
                Data sharing is a stored preference only. No wellness data leaves
                your account in this build.
              </p>

              {deleteOpen && (
                <form
                  onSubmit={deleteAccount}
                  className="mt-5 rounded-xl border border-rose-400/20 bg-rose-400/5 p-5"
                >
                  <p className="text-sm text-rose-200 mb-3">
                    This cannot be undone. Enter your password to confirm.
                  </p>
                  <TextField
                    label="Password"
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    required
                  />
                  {deleteError && (
                    <p className="text-sm text-rose-300 mt-3">{deleteError}</p>
                  )}
                  <div className="flex gap-3 mt-4">
                    <Button type="submit" variant="secondary" className="!text-rose-300" disabled={deleting}>
                      {deleting ? 'Deleting...' : 'Delete permanently'}
                    </Button>
                    <Button type="button" variant="ghost" onClick={() => setDeleteOpen(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              )}

              <Status status={prefsStatus} />
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  )
}
