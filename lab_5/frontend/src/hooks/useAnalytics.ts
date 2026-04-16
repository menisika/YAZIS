import { useQuery } from '@tanstack/react-query'
import api from '../config/api'

export interface AnalyticsSummary {
  total_sessions: number
  total_duration_minutes: number
  total_volume_kg: number
  total_calories: number
  current_streak: number
  sessions_this_week: number
}

export interface WeeklyFrequency {
  week: string
  count: number
}

export interface MuscleDistribution {
  muscle_group: string
  total_sets: number
  total_volume_kg: number
}

export interface ExerciseProgression {
  date: string
  max_weight_kg: number
  total_volume_kg: number
  total_reps: number
}

export interface CalorieEntry {
  date: string
  calories: number
}

export function useAnalyticsSummary(period = 30) {
  return useQuery<AnalyticsSummary>({
    queryKey: ['analytics', 'summary', period],
    queryFn: async () => {
      const { data } = await api.get('/analytics/summary', { params: { period } })
      return data
    },
  })
}

export function useWeeklyFrequency(weeks = 12) {
  return useQuery<WeeklyFrequency[]>({
    queryKey: ['analytics', 'frequency', weeks],
    queryFn: async () => {
      const { data } = await api.get('/analytics/frequency', { params: { weeks } })
      return data
    },
  })
}

export function useMuscleDistribution(period = 30) {
  return useQuery<MuscleDistribution[]>({
    queryKey: ['analytics', 'muscle-distribution', period],
    queryFn: async () => {
      const { data } = await api.get('/analytics/muscle-distribution', { params: { period } })
      return data
    },
  })
}

export function useExerciseProgression(exerciseId: number | null, period = 90) {
  return useQuery<ExerciseProgression[]>({
    queryKey: ['analytics', 'progression', exerciseId, period],
    queryFn: async () => {
      const { data } = await api.get('/analytics/progression', {
        params: { exercise_id: exerciseId, period },
      })
      return data
    },
    enabled: !!exerciseId,
  })
}

export function useCalorieHistory(period = 30) {
  return useQuery<CalorieEntry[]>({
    queryKey: ['analytics', 'calories', period],
    queryFn: async () => {
      const { data } = await api.get('/analytics/calories', { params: { period } })
      return data
    },
  })
}
