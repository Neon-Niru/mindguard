import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Lock, ArrowRight, CheckCircle2 } from 'lucide-react'
import AuthShell from '../components/layout/AuthShell.jsx'
import TextField from '../components/ui/TextField.jsx'
import Button from '../components/ui/Button.jsx'
import { auth } from '../services/api'

export default function ResetPassword() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const token = params.get('token') || ''

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    const password = e.target.password.value
    const confirm = e.target.confirm.value

    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)

    try {
      await auth.resetPassword(token, password)
      setDone(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="Choose a new password"
      subtitle={
        token
          ? 'Enter a new password for your account.'
          : 'This reset link is incomplete. Request a new one.'
      }
      footer={
        <>
          Back to{' '}
          <Link to="/login" className="text-accent-purple hover:text-accent-teal transition-colors">
            login
          </Link>
        </>
      }
    >
      {done ? (
        <div className="text-center py-4">
          <div className="w-12 h-12 rounded-full bg-accent-teal/10 border border-accent-teal/25 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 size={22} className="text-accent-teal" />
          </div>
          <p className="text-sm text-text-hi mb-4">Your password has been updated.</p>
          <Button variant="primary" onClick={() => navigate('/login')}>
            Go to login
          </Button>
        </div>
      ) : !token ? (
        <div className="text-center py-4">
          <p className="text-sm text-text-lo mb-5">
            Reset links expire after one hour. Request a fresh link to continue.
          </p>
          <Link
            to="/forgot-password"
            className="inline-flex items-center gap-2 text-sm text-accent-purple hover:text-accent-teal"
          >
            Request a new link <ArrowRight size={14} />
          </Link>
        </div>
      ) : (
        <form className="space-y-5" onSubmit={handleSubmit}>
          {error && (
            <p className="text-sm text-rose-300 bg-rose-300/10 rounded-lg px-4 py-2">{error}</p>
          )}
          <TextField
            label="New password"
            type="password"
            name="password"
            placeholder="At least 6 characters"
            icon={Lock}
            minLength={6}
            required
          />
          <TextField
            label="Confirm new password"
            type="password"
            name="confirm"
            placeholder="Repeat your new password"
            icon={Lock}
            minLength={6}
            required
          />
          <Button type="submit" variant="primary" icon={ArrowRight} className="w-full" disabled={loading}>
            {loading ? 'Updating...' : 'Update Password'}
          </Button>
        </form>
      )}
    </AuthShell>
  )
}
