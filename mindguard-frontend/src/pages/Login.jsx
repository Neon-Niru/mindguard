import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, ArrowRight } from 'lucide-react'
import AuthShell from '../components/layout/AuthShell.jsx'
import TextField from '../components/ui/TextField.jsx'
import Button from '../components/ui/Button.jsx'
import { auth } from '../services/api'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const form = e.target
    const email = form.email.value
    const password = form.password.value

    try {
      const data = await auth.login(email, password)
      login(data.token, data.user)
      navigate('/app/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to check in on your wellness."
      footer={
        <>
          New to MindGuard AI?{' '}
          <Link to="/register" className="text-accent-purple hover:text-accent-teal transition-colors">
            Create an account
          </Link>
        </>
      }
    >
      <form className="space-y-5" onSubmit={handleSubmit}>
        {error && (
          <p className="text-sm text-rose-300 bg-rose-300/10 rounded-lg px-4 py-2">{error}</p>
        )}
        <TextField label="Email" type="email" name="email" placeholder="you@school.edu" icon={Mail} required />
        <TextField label="Password" type="password" name="password" placeholder="••••••••" icon={Lock} required />

        <div className="flex items-center justify-between text-xs">
          <label className="flex items-center gap-2 text-text-lo">
            <input type="checkbox" className="rounded border-white/20 bg-white/5" />
            Remember me
          </label>
          <Link to="/forgot-password" className="text-accent-purple hover:text-accent-teal transition-colors">
            Forgot password?
          </Link>
        </div>

        <Button type="submit" variant="primary" icon={ArrowRight} className="w-full" disabled={loading}>
          {loading ? 'Logging in...' : 'Log In'}
        </Button>
      </form>
    </AuthShell>
  )
}
