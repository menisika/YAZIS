import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import {
  LayoutDashboard,
  ClipboardList,
  ScrollText,
  BarChart3,
  Dumbbell,
  User,
  LogOut,
  MessageSquare,
} from 'lucide-react'
import { Separator } from '@/components/ui/separator'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/plan', label: 'Workout Plan', icon: ClipboardList },
  { path: '/history', label: 'History', icon: ScrollText },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/exercises', label: 'Exercises', icon: Dumbbell },
  { path: '/assistant', label: 'AI Assistant', icon: MessageSquare },
  { path: '/profile', label: 'Profile', icon: User },
]

export default function Sidebar() {
  const { user, signOut } = useAuthStore()

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-card border-r border-border h-screen sticky top-0">
      <div className="p-6">
        <h1 className="text-xl font-bold text-primary tracking-tight">FitPlanner AI</h1>
        <p className="text-sm text-muted-foreground mt-1 truncate">{user?.display_name || user?.email}</p>
      </div>

      <Separator />

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`
            }
          >
            <item.icon className="h-4 w-4" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <Separator />

      <div className="p-3">
        <button
          onClick={() => signOut()}
          className="flex items-center gap-3 w-full px-4 py-2.5 rounded-xl text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors cursor-pointer"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
