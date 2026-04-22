import { useState } from 'react'
import { MessageCircle, Plus, Trash2 } from 'lucide-react'
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
      <aside
        className="w-64 shrink-0 flex-col hidden sm:flex"
        style={{ background: '#0A0A0A', borderRight: '1px solid rgba(255,255,255,0.06)' }}
      >
        <div className="p-4" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <button
            type="button"
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-2xl font-bold text-sm"
            style={{ background: 'rgba(173,255,47,0.12)', color: '#ADFF2F' }}
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {!conversations || conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full gap-2 p-4">
              <MessageCircle className="h-8 w-8 opacity-30 text-white" />
              <p className="text-center text-sm" style={{ color: '#8E8E93' }}>No conversations yet.</p>
            </div>
          ) : (
            <ul>
              {conversations.map((conv) => (
                <li
                  key={conv.id}
                  className="group relative"
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                >
                  <button
                    type="button"
                    className="w-full text-left px-4 py-3 pr-10 transition-colors"
                    style={
                      conv.id === conversationId
                        ? { background: 'rgba(173,255,47,0.08)' }
                        : {}
                    }
                    onMouseEnter={(e) => {
                      if (conv.id !== conversationId) e.currentTarget.style.background = 'rgba(255,255,255,0.03)'
                    }}
                    onMouseLeave={(e) => {
                      if (conv.id !== conversationId) e.currentTarget.style.background = 'transparent'
                    }}
                    onClick={() => setConversationId(conv.id)}
                  >
                    <p className="text-sm font-medium truncate text-white">
                      {conv.title ?? 'Untitled chat'}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: '#8E8E93' }}>
                      {formatDate(conv.created_at)} · {conv.message_count} msgs
                    </p>
                  </button>
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1.5 rounded-lg transition-all"
                    style={{ color: '#FF375F' }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,55,95,0.1)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
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
      <div className="flex flex-col flex-1 min-w-0 bg-black">
        {/* Mobile: conversation switcher */}
        <div
          className="sm:hidden flex items-center gap-2 p-3"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', background: '#1C1C1E' }}
        >
          <button
            type="button"
            onClick={handleNewChat}
            className="flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-semibold"
            style={{ background: 'rgba(173,255,47,0.12)', color: '#ADFF2F' }}
          >
            <Plus className="h-4 w-4" /> New
          </button>
          {conversations && conversations.length > 0 && (
            <select
              className="flex-1 text-sm rounded-xl px-2 py-1.5 text-white outline-none"
              style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.06)' }}
              value={conversationId ?? ''}
              onChange={(e) => setConversationId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">New conversation</option>
              {conversations.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title ?? 'Untitled'} ({c.message_count})
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
