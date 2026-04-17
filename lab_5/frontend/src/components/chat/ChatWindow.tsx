import { useState, useRef, useEffect } from 'react'
import { Loader2, Send } from 'lucide-react'
import ChatBubble from './ChatBubble'
import { useSendMessage, useConversation, type ChatMessage } from '../../hooks/useChat'

interface ChatWindowProps {
  conversationId: number | null
  onConversationCreated?: (id: number) => void
}

export default function ChatWindow({ conversationId, onConversationCreated }: ChatWindowProps) {
  const [input, setInput] = useState('')
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const sendMessage = useSendMessage()

  const { data: conversation } = useConversation(conversationId)

  useEffect(() => {
    setLocalMessages([])
    setInput('')
  }, [conversationId])

  const messages = conversation?.messages ?? localMessages

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || sendMessage.isPending) return

    const userMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      created_at: new Date().toISOString(),
    }
    setLocalMessages((prev) => [...prev, userMsg])
    setInput('')

    try {
      const result = await sendMessage.mutateAsync({
        conversation_id: conversationId,
        message: input,
      })
      if (!conversationId && onConversationCreated) {
        onConversationCreated(result.conversation_id)
      }
      setLocalMessages((prev) => [...prev, result.message])
    } catch {
      setLocalMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
          created_at: new Date().toISOString(),
        },
      ])
    }
  }

  return (
    <div className="flex flex-col h-full bg-black">
      <div className="flex-1 overflow-y-auto p-4 space-y-1">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <p className="text-lg text-white mb-2">Ask me anything about fitness!</p>
            <p className="text-sm" style={{ color: '#8E8E93' }}>
              I can help with exercises, nutrition, recovery, and workout adjustments.
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatBubble key={msg.id} role={msg.role} content={msg.content} timestamp={msg.created_at} />
        ))}
        {sendMessage.isPending && (
          <div className="flex justify-start mb-3">
            <div className="px-4 py-3 rounded-2xl" style={{ background: '#1C1C1E', borderBottomLeftRadius: 4 }}>
              <Loader2 className="h-4 w-4 animate-spin" style={{ color: '#8E8E93' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend() }}
          className="flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about fitness, nutrition, recovery…"
            disabled={sendMessage.isPending}
            className="flex-1 px-4 py-2.5 rounded-2xl text-sm text-white placeholder-[#636366] outline-none"
            style={{ background: '#1C1C1E', border: '1px solid rgba(255,255,255,0.08)' }}
            onFocus={(e) => (e.target.style.borderColor = 'rgba(173,255,47,0.4)')}
            onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.08)')}
          />
          <button
            type="submit"
            disabled={!input.trim() || sendMessage.isPending}
            className="flex items-center justify-center w-10 h-10 rounded-2xl transition-all shrink-0"
            style={
              input.trim() && !sendMessage.isPending
                ? { background: '#ADFF2F', cursor: 'pointer' }
                : { background: '#1C1C1E', cursor: 'not-allowed' }
            }
          >
            {sendMessage.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" style={{ color: '#8E8E93' }} />
            ) : (
              <Send className="h-4 w-4" style={{ color: input.trim() ? '#000' : '#8E8E93' }} />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
