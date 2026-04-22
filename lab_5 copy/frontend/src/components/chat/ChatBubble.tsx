interface ChatBubbleProps {
  role: string
  content: string
  timestamp?: string
}

export default function ChatBubble({ role, content, timestamp }: ChatBubbleProps) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div
        className="max-w-[80%] px-4 py-3 rounded-2xl"
        style={
          isUser
            ? { background: '#ADFF2F', color: '#000', borderBottomRightRadius: 4 }
            : { background: '#1C1C1E', color: '#fff', borderBottomLeftRadius: 4 }
        }
      >
        <p className="text-sm whitespace-pre-wrap">{content}</p>
        {timestamp && (
          <p
            className="text-xs mt-1"
            style={{ color: isUser ? 'rgba(0,0,0,0.5)' : '#8E8E93' }}
          >
            {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  )
}
