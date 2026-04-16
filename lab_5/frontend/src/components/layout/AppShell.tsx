import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import MobileNav from './MobileNav'

export default function AppShell() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 pb-20 lg:pb-0">
        <div className="max-w-6xl mx-auto p-4 lg:p-8">
          <Outlet />
        </div>
      </main>
      <MobileNav />
    </div>
  )
}
