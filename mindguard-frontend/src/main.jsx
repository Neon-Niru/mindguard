import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, useNavigate } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

function RedirectHandler({ children }) {
  const navigate = useNavigate()
  useEffect(() => {
    const redirect = sessionStorage.getItem('redirect')
    if (redirect) {
      sessionStorage.removeItem('redirect')
      navigate(redirect.replace('/mindguard', '') || '/', { replace: true })
    }
  }, [navigate])
  return children
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename="/mindguard">
      <RedirectHandler>
        <App />
      </RedirectHandler>
    </BrowserRouter>
  </React.StrictMode>,
)
