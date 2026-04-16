import { useState } from 'react'
import { MessageCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import ChatWindow from './ChatWindow'
import { useAuthStore } from '../../stores/authStore'

export default function ChatFAB() {
  const [isOpen, setIsOpen] = useState(false)
  const [conversationId, setConversationId] = useState<number | null>(null)
  const { user } = useAuthStore()

  if (!user) return null

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-24 right-6 lg:bottom-8 lg:right-8 z-50 w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center hover:scale-105 transition-transform cursor-pointer"
      >
        {isOpen ? <X className="h-5 w-5" /> : <MessageCircle className="h-5 w-5" />}
      </button>

      {isOpen && (
        <div className="fixed bottom-40 right-6 lg:bottom-24 lg:right-8 z-50 w-[360px] h-[500px] bg-card rounded-2xl shadow-2xl border border-border flex flex-col overflow-hidden">
          <div className="bg-primary text-primary-foreground px-4 py-3 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm">AI Fitness Assistant</h3>
              <p className="text-xs opacity-80">Ask me anything</p>
            </div>
            <Button
              size="sm"
              variant="ghost"
              className="text-primary-foreground hover:bg-white/20"
              onClick={() => setConversationId(null)}
            >
              New Chat
            </Button>
          </div>
          <ChatWindow
            conversationId={conversationId}
            onConversationCreated={setConversationId}
          />
        </div>
      )}
    </>
  )
}
