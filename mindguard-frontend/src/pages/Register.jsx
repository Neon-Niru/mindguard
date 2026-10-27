import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, Mail, Lock, ArrowRight } from 'lucide-react'
import AuthShell from '../components/layout/AuthShell.jsx'
import TextField from '../components/ui/TextField.jsx'
import Button from '../components/ui/Button.jsx'
import { auth } from '../services/api'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const form = e.target
    const name = form.name.value
    const email = form.email.value
    const password = form.password.value

    try {
      const data = await auth.register(name, email, password)
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
      title="Create your account"
      subtitle="Start your wellness journey in under a minute."
      footer={
        <>
          Already have an account?{' '}
          <Link to="/login" className="text-accent-purple hover:text-accent-teal transition-colors">
            Log in
          </Link>
        </>
      }
    >
      <form className="space-y-5" onSubmit={handleSubmit}>
        {error && (
          <p className="text-sm text-rose-300 bg-rose-300/10 rounded-lg px-4 py-2">{error}</p>
        )}
        <TextField label="Full name" type="text" name="name" placeholder="Aditi Sharma" icon={User} required />
        <TextField label="Email" type="email" name="email" placeholder="you@school.edu" icon={Mail} required />
        <TextField label="Password" type="password" name="password" placeholder="At least 6 characters" icon={Lock} required />

        <label className="flex items-start gap-2.5 text-xs text-text-lo">
          <input type="checkbox" className="mt-0.5 rounded border-white/20 bg-white/5" required />
          I agree to the Terms of Service and Privacy Policy.
        </label>

        <Button type="submit" variant="primary" icon={ArrowRight} className="w-full" disabled={loading}>
          {loading ? 'Creating account...' : 'Create Account'}
        </Button>
      </form>
    </AuthShell>
  )
}
