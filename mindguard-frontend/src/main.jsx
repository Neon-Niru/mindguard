import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, useNavigate } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

const base = import.meta.env.BASE_URL || '/'
const routerBasename = base === '/' ? undefined : base.replace(/\/$/, '')

function RedirectHandler({ children }) {
  const navigate = useNavigate()

  useEffect(() => {
    const redirect = sessionStorage.getItem('redirect')
    if (!redirect) return

    sessionStorage.removeItem('redirect')

    let target = redirect
    if (routerBasename && target.startsWith(routerBasename)) {
      target = target.slice(routerBasename.length)
    }

    navigate(target.startsWith('/') ? target : `/${target}`, { replace: true })
  }, [navigate])

  return children
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename={routerBasename}>
      <RedirectHandler>
        <App />
      </RedirectHandler>
    </BrowserRouter>
  </React.StrictMode>,
)
