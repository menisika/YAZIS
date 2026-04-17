import { useState, useRef, useEffect } from 'react'
import { Loader2, Send } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
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

  // Reset local messages whenever we switch conversations
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
        { id: Date.now(), role: 'assistant', content: 'Sorry, something went wrong. Please try again.', created_at: new Date().toISOString() },
      ])
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-1">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground py-8">
            <p className="text-lg mb-2">Ask me anything about fitness!</p>
            <p className="text-sm">I can help with exercises, nutrition, recovery, and workout adjustments.</p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatBubble key={msg.id} role={msg.role} content={msg.content} timestamp={msg.created_at} />
        ))}
        {sendMessage.isPending && (
          <div className="flex justify-start mb-3">
            <div className="bg-muted rounded-2xl px-4 py-3 rounded-bl-md">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-border">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about fitness, nutrition, recovery..."
            className="flex-1"
            disabled={sendMessage.isPending}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || sendMessage.isPending}
          >
            {sendMessage.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}
