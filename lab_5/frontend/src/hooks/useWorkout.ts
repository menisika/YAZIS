import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'

export interface PlanExercise {
  id: number
  exercise_id: number
  exercise_name: string | null
  exercise_description: string | null
  sets: number
  reps_min: number
  reps_max: number
  rest_seconds: number
  order_index: number
  notes: string | null
}

export type PlanDayStatus = 'rest' | 'done' | 'today' | 'skipped' | 'upcoming'

export interface PlanDay {
  plan_id: number
  day_of_week: number
  focus: string
  is_rest: boolean
  status: PlanDayStatus
  exercises: PlanExercise[]
}

export interface WorkoutPlan {
  id: number
  user_id: number
  name: string
  plan_type: string
  created_at: string
  valid_from: string | null
  valid_to: string | null
  days: PlanDay[]
}

export function useWorkoutPlans() {
  return useQuery<WorkoutPlan[]>({
    queryKey: ['workouts'],
    queryFn: async () => {
      const { data } = await api.get('/workouts')
      return data
    },
  })
}

export function useWorkoutPlan(planId: number | null) {
  return useQuery<WorkoutPlan>({
    queryKey: ['workouts', planId],
    queryFn: async () => {
      const { data } = await api.get(`/workouts/${planId}`)
      return data
    },
    enabled: !!planId,
  })
}

export function useTodayWorkout() {
  return useQuery<PlanDay | null>({
    queryKey: ['workouts', 'today'],
    queryFn: async () => {
      const { data } = await api.get('/workouts/today')
      return data
    },
  })
}

export function useGenerateWorkout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (params: {
      week_start?: string
      focus_muscle_groups?: string[]
      exclude_exercises?: number[]
    }) => {
      const { data } = await api.post('/workouts/generate', params)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    },
  })
}

export function useSwapDays() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (params: { day_a: number; day_b: number }) => {
      const { data } = await api.patch('/workouts/plan/days/swap', params)
      return data as WorkoutPlan
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    },
  })
}

export function useToggleRest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (dayOfWeek: number) => {
      const { data } = await api.patch(`/workouts/plan/days/${dayOfWeek}/toggle-rest`)
      return data as WorkoutPlan
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    },
  })
}

export function useDeleteWorkout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (planId: number) => {
      await api.delete(`/workouts/${planId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    },
  })
}
