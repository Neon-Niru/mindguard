import { lazy, Suspense, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import AppLayout from './components/layout/AppLayout.jsx'

// Route-level code splitting keeps the first paint light (the charts and the
// settings screens are only downloaded when they are opened).
const Landing = lazy(() => import('./pages/Landing.jsx'))
const Login = lazy(() => import('./pages/Login.jsx'))
const Register = lazy(() => import('./pages/Register.jsx'))
const ForgotPassword = lazy(() => import('./pages/ForgotPassword.jsx'))
const ResetPassword = lazy(() => import('./pages/ResetPassword.jsx'))
const NotFound = lazy(() => import('./pages/NotFound.jsx'))
const Dashboard = lazy(() => import('./pages/Dashboard.jsx'))
const AIChat = lazy(() => import('./pages/AIChat.jsx'))
const Planner = lazy(() => import('./pages/Planner.jsx'))
const Progress = lazy(() => import('./pages/Progress.jsx'))
const Settings = lazy(() => import('./pages/Settings.jsx'))

function FullPageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-text-lo">Loading MindGuard...</p>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) return <FullPageLoader />

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}

// Handles deep links like /#features after lazy content mounts, and resets
// scroll when moving between pages of the app.
function ScrollManager() {
  const { pathname, hash } = useLocation()

  useEffect(() => {
    if (hash) {
      const id = decodeURIComponent(hash.slice(1))
      let attempts = 0

      // The landing sections are lazy-loaded, so retry briefly until the
      // anchor exists instead of silently doing nothing.
      const timer = window.setInterval(() => {
        const target = document.getElementById(id)

        if (target) {
          window.clearInterval(timer)
          const top = target.getBoundingClientRect().top + window.scrollY - 96
          window.scrollTo({ top, behavior: 'smooth' })
        } else if (++attempts > 40) {
          window.clearInterval(timer)
        }
      }, 50)

      return () => window.clearInterval(timer)
    }

    window.scrollTo({ top: 0, behavior: 'auto' })
    return undefined
  }, [pathname, hash])

  return null
}

function AppRoutes() {
  return (
    <Suspense fallback={<FullPageLoader />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        <Route path="/app" element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<AIChat />} />
          <Route path="planner" element={<Planner />} />
          <Route path="progress" element={<Progress />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <ScrollManager />
      <AppRoutes />
    </AuthProvider>
  )
}
