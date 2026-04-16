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
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-md'
            : 'bg-muted text-foreground rounded-bl-md'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{content}</p>
        {timestamp && (
          <p className={`text-xs mt-1 ${isUser ? 'text-primary-foreground/60' : 'text-muted-foreground'}`}>
            {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  )
}
