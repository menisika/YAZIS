import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ClipboardList,
  ScrollText,
  MessageSquare,
  User,
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Home', icon: LayoutDashboard },
  { path: '/plan', label: 'Plan', icon: ClipboardList },
  { path: '/history', label: 'History', icon: ScrollText },
  { path: '/assistant', label: 'Assistant', icon: MessageSquare },
  { path: '/profile', label: 'Profile', icon: User },
]

export default function MobileNav() {
  return (
    <nav
      className="lg:hidden fixed bottom-4 left-3 right-3 z-50"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      <div
        className="flex justify-around items-center py-2 px-1 rounded-full shadow-2xl"
        style={{ background: '#1C1C1E', backdropFilter: 'blur(20px)' }}
      >
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className="flex-1"
          >
            {({ isActive }) => (
              <div className="flex flex-col items-center gap-0.5 px-2 py-1.5 transition-all">
                <div
                  className="flex items-center justify-center w-9 h-9 rounded-full transition-all"
                  style={isActive ? { background: 'rgba(173,255,47,0.15)' } : {}}
                >
                  <item.icon
                    className="h-5 w-5 transition-colors"
                    style={{ color: isActive ? '#ADFF2F' : '#8E8E93' }}
                  />
                </div>
                <span
                  className="text-[10px] font-medium transition-colors"
                  style={{ color: isActive ? '#ADFF2F' : '#8E8E93' }}
                >
                  {item.label}
                </span>
              </div>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
