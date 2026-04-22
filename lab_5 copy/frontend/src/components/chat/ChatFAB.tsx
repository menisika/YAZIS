import { MessageCircle } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

export default function ChatFAB() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  if (!user || location.pathname === '/assistant') return null

  return (
    <button
      onClick={() => navigate('/assistant')}
      className="fixed bottom-24 right-6 lg:bottom-8 lg:right-8 z-50 w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center hover:scale-105 transition-transform cursor-pointer"
      title="Open AI Assistant"
    >
      <MessageCircle className="h-5 w-5" />
    </button>
  )
}
