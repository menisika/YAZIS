import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'

export interface ChatMessage {
  id: number
  role: string
  content: string
  created_at: string
}

export interface ChatConversation {
  id: number
  title: string | null
  created_at: string
  messages: ChatMessage[]
}

export interface ChatConversationItem {
  id: number
  title: string | null
  created_at: string
  message_count: number
}

export function useConversations() {
  return useQuery<ChatConversationItem[]>({
    queryKey: ['chat', 'conversations'],
    queryFn: async () => {
      const { data } = await api.get('/chat/conversations')
      return data
    },
  })
}

export function useConversation(conversationId: number | null) {
  return useQuery<ChatConversation>({
    queryKey: ['chat', 'conversations', conversationId],
    queryFn: async () => {
      const { data } = await api.get(`/chat/conversations/${conversationId}`)
      return data
    },
    enabled: !!conversationId,
  })
}

export function useSendMessage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      conversation_id,
      message,
    }: {
      conversation_id: number | null
      message: string
    }) => {
      const { data } = await api.post('/chat/send', { conversation_id, message })
      return data as { conversation_id: number; message: ChatMessage }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chat', 'conversations'] })
      queryClient.invalidateQueries({
        queryKey: ['chat', 'conversations', data.conversation_id],
      })
    },
  })
}

export function useDeleteConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (conversationId: number) => {
      await api.delete(`/chat/conversations/${conversationId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat', 'conversations'] })
    },
  })
}
