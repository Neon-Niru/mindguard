import { Outlet } from 'react-router-dom'
import AppSidebar from './AppSidebar.jsx'
import MobileNav from './MobileNav.jsx'

export default function AppLayout() {
  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <main className="flex-1 min-w-0 px-5 md:px-8 py-6 md:py-8 pb-28 md:pb-8">
        <Outlet />
      </main>
      <MobileNav />
    </div>
  )
}
