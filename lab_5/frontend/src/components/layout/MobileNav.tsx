import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ClipboardList,
  ScrollText,
  BarChart3,
  User,
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Home', icon: LayoutDashboard },
  { path: '/plan', label: 'Plan', icon: ClipboardList },
  { path: '/history', label: 'History', icon: ScrollText },
  { path: '/analytics', label: 'Stats', icon: BarChart3 },
  { path: '/profile', label: 'Profile', icon: User },
]

export default function MobileNav() {
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-card border-t border-border z-50 pb-[env(safe-area-inset-bottom)]">
      <div className="flex justify-around py-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 px-3 py-2 text-xs transition-colors min-w-[48px] ${
                isActive ? 'text-primary' : 'text-muted-foreground'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
