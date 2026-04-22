import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import MobileNav from './MobileNav'

export default function AppShell() {
  return (
    <div className="dark flex min-h-screen bg-black">
      <Sidebar />
      <main className="flex-1 pb-28 lg:pb-0">
        <div className="max-w-6xl mx-auto p-4 lg:p-8">
          <Outlet />
        </div>
      </main>
      <MobileNav />
    </div>
  )
}
