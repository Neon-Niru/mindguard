import { Link } from 'react-router-dom'
import { Brain, Home } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="w-14 h-14 rounded-2xl bg-brand-gradient flex items-center justify-center mx-auto mb-5">
          <Brain size={24} className="text-white" />
        </div>
        <p className="text-xs uppercase tracking-widest text-accent-purple mb-2">404</p>
        <h1 className="text-2xl font-display font-semibold mb-3">Page not found</h1>
        <p className="text-sm text-text-lo mb-7">
          The page you are looking for doesn't exist or may have moved.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 bg-brand-gradient rounded-full px-6 py-3 text-sm font-medium text-white shadow-glow-sm hover:brightness-110 transition-all"
        >
          <Home size={16} />
          Back to Home
        </Link>
      </div>
    </div>
  )
}
