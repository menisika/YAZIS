import { useState } from 'react'
import { MessageCircle, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import ChatWindow from '../components/chat/ChatWindow'
import { useConversations, useDeleteConversation } from '../hooks/useChat'

export default function AssistantPage() {
  const [conversationId, setConversationId] = useState<number | null>(null)
  const { data: conversations } = useConversations()
  const deleteConversation = useDeleteConversation()

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  }

  const handleNewChat = () => setConversationId(null)

  return (
    <div className="flex h-[calc(100vh-4rem)] lg:h-[calc(100vh-2rem)] -m-4 lg:-m-6 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 border-r border-border flex flex-col bg-card hidden sm:flex">
        <div className="p-4 border-b border-border">
          <Button className="w-full" onClick={handleNewChat} size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {!conversations || conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm gap-2 p-4">
              <MessageCircle className="h-8 w-8 opacity-30" />
              <p className="text-center">No conversations yet. Start one!</p>
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {conversations.map((conv) => (
                <li key={conv.id} className="group relative">
                  <button
                    className={`w-full text-left px-4 py-3 hover:bg-muted transition-colors pr-10 ${
                      conv.id === conversationId ? 'bg-primary/10' : ''
                    }`}
                    onClick={() => setConversationId(conv.id)}
                  >
                    <p className="text-sm font-medium truncate">
                      {conv.title ?? 'Untitled chat'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {formatDate(conv.created_at)} · {conv.message_count} messages
                    </p>
                  </button>
                  <button
                    className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-destructive/10 text-destructive transition-all"
                    onClick={() => {
                      deleteConversation.mutate(conv.id)
                      if (conversationId === conv.id) setConversationId(null)
                    }}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* Chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Mobile: conversation switcher */}
        <div className="sm:hidden flex items-center gap-2 p-3 border-b border-border bg-card">
          <Button size="sm" onClick={handleNewChat}>
            <Plus className="h-4 w-4 mr-1" />
            New
          </Button>
          {conversations && conversations.length > 0 && (
            <select
              className="flex-1 text-sm border border-border rounded-lg px-2 py-1 bg-background"
              value={conversationId ?? ''}
              onChange={(e) => setConversationId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">New conversation</option>
              {conversations.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title ?? 'Untitled chat'} ({c.message_count})
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="flex-1 overflow-hidden">
          <ChatWindow
            conversationId={conversationId}
            onConversationCreated={setConversationId}
          />
        </div>
      </div>
    </div>
  )
}
