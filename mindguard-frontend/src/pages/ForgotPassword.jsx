import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Mail, ArrowRight, CheckCircle2 } from 'lucide-react'
import AuthShell from '../components/layout/AuthShell.jsx'
import TextField from '../components/ui/TextField.jsx'
import Button from '../components/ui/Button.jsx'
import { auth } from '../services/api'

export default function ForgotPassword() {
  const [sent, setSent] = useState(false)
  const [resetToken, setResetToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await auth.forgotPassword(e.target.email.value)
      setResetToken(data.reset_token || '')
      setSent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="Reset your password"
      subtitle="We'll help you get back into your account."
      footer={
        <>
          Remembered it?{' '}
          <Link to="/login" className="text-accent-purple hover:text-accent-teal transition-colors">
            Back to login
          </Link>
        </>
      }
    >
      {sent ? (
        <div className="text-center py-4">
          <div className="w-12 h-12 rounded-full bg-accent-teal/10 border border-accent-teal/25 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 size={22} className="text-accent-teal" />
          </div>
          <p className="text-sm text-text-hi mb-1.5">Check your inbox</p>
          <p className="text-sm text-text-lo">
            If an account exists for that email, a reset link is on its way.
            The link expires in one hour.
          </p>

          {resetToken && (
            <div className="mt-6 rounded-xl bg-white/5 border border-white/10 p-4 text-left">
              <p className="text-xs text-text-faint mb-2">
                Demo mode: email delivery is not configured, so use this link.
              </p>
              <Link
                to={`/reset-password?token=${encodeURIComponent(resetToken)}`}
                className="text-sm text-accent-purple hover:text-accent-teal break-all"
              >
                Continue to reset password →
              </Link>
            </div>
          )}
        </div>
      ) : (
        <form className="space-y-5" onSubmit={handleSubmit}>
          {error && (
            <p className="text-sm text-rose-300 bg-rose-300/10 rounded-lg px-4 py-2">{error}</p>
          )}
          <TextField label="Email" type="email" name="email" placeholder="you@school.edu" icon={Mail} required />
          <Button type="submit" variant="primary" icon={ArrowRight} className="w-full" disabled={loading}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </Button>
        </form>
      )}
    </AuthShell>
  )
}
