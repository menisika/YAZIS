import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'

export interface SessionSet {
  id: number
  exercise_id: number
  exercise_name: string | null
  set_number: number
  weight_kg: number | null
  reps: number
  duration_seconds: number | null
  rpe: number | null
  completed_at: string
}

export interface WorkoutSession {
  id: number
  user_id: number
  plan_id: number | null
  plan_day_of_week: number | null
  started_at: string
  ended_at: string | null
  duration_seconds: number | null
  status: string
  estimated_calories: number | null
  notes: string | null
  sets: SessionSet[]
}

export function useSessions(offset = 0, limit = 20) {
  return useQuery<WorkoutSession[]>({
    queryKey: ['sessions', offset, limit],
    queryFn: async () => {
      const { data } = await api.get('/sessions', { params: { offset, limit } })
      return data
    },
  })
}

export function useSessionDetail(sessionId: number | null) {
  return useQuery<WorkoutSession>({
    queryKey: ['sessions', sessionId],
    queryFn: async () => {
      const { data } = await api.get(`/sessions/${sessionId}`)
      return data
    },
    enabled: !!sessionId,
  })
}

export function useStartSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (params: { plan_id?: number; plan_day_of_week?: number; notes?: string }) => {
      const { data } = await api.post('/sessions', params)
      return data as WorkoutSession
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    },
  })
}

export function useEndSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      sessionId,
      status,
      notes,
    }: {
      sessionId: number
      status: string
      notes?: string
    }) => {
      const { data } = await api.patch(`/sessions/${sessionId}`, { status, notes })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    },
  })
}

export function useLogSet() {
  return useMutation({
    mutationFn: async ({
      sessionId,
      ...setData
    }: {
      sessionId: number
      exercise_id: number
      set_number: number
      weight_kg?: number | null
      reps: number
      rpe?: number | null
    }) => {
      const { data } = await api.post(`/sessions/${sessionId}/sets`, setData)
      return data
    },
  })
}
