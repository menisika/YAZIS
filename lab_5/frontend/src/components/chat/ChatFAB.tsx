import { useState } from 'react'
import { MessageCircle, X, ChevronLeft, Plus, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import ChatWindow from './ChatWindow'
import { useAuthStore } from '../../stores/authStore'
import { useConversations } from '../../hooks/useChat'

type View = 'chat' | 'history'

export default function ChatFAB() {
  const [isOpen, setIsOpen] = useState(false)
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [view, setView] = useState<View>('chat')
  const { user } = useAuthStore()
  const { data: conversations } = useConversations()

  if (!user) return null

  const handleSelectConversation = (id: number) => {
    setConversationId(id)
    setView('chat')
  }

  const handleNewChat = () => {
    setConversationId(null)
    setView('chat')
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  }

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
          {/* Header */}
          <div className="bg-primary text-primary-foreground px-4 py-3 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              {view === 'history' && (
                <button
                  onClick={() => setView('chat')}
                  className="hover:bg-white/20 rounded p-0.5 transition-colors"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
              )}
              <div>
                <h3 className="font-semibold text-sm">
                  {view === 'history' ? 'Chat History' : 'AI Fitness Assistant'}
                </h3>
                <p className="text-xs opacity-80">
                  {view === 'history' ? 'Select a conversation' : 'Ask me anything'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {view === 'chat' && (
                <>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-primary-foreground hover:bg-white/20 h-7 w-7 p-0"
                    onClick={() => setView('history')}
                    title="Chat history"
                  >
                    <Clock className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-primary-foreground hover:bg-white/20"
                    onClick={handleNewChat}
                  >
                    <Plus className="h-3.5 w-3.5 mr-1" />
                    New
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Body */}
          {view === 'history' ? (
            <div className="flex-1 overflow-y-auto">
              {!conversations || conversations.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm gap-2">
                  <MessageCircle className="h-8 w-8 opacity-30" />
                  <p>No previous conversations</p>
                  <Button variant="outline" size="sm" onClick={handleNewChat}>
                    Start a chat
                  </Button>
                </div>
              ) : (
                <ul className="divide-y divide-border">
                  {conversations.map((conv) => (
                    <li key={conv.id}>
                      <button
                        className="w-full text-left px-4 py-3 hover:bg-muted transition-colors"
                        onClick={() => handleSelectConversation(conv.id)}
                      >
                        <p className="text-sm font-medium truncate">
                          {conv.title ?? 'Untitled chat'}
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {formatDate(conv.created_at)} · {conv.message_count} messages
                        </p>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <ChatWindow
              conversationId={conversationId}
              onConversationCreated={setConversationId}
            />
          )}
        </div>
      )}
    </>
  )
}
