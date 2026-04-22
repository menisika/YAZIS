import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'

interface UserProfile {
  id: number
  user_id: number
  age: number
  gender: string
  height_cm: number
  weight_kg: number
  fitness_level: string
  preferred_workout_types: string[]
  workout_days_per_week: number
  session_duration_min: number
  bmr: number
  tdee: number
  injuries: string[]
  calorie_goal: number
  updated_at: string
}

interface ProfileInput {
  age: number
  gender: string
  height_cm: number
  weight_kg: number
  fitness_level: string
  preferred_workout_types: string[]
  workout_days_per_week: number
  session_duration_min: number
  injuries: string[]
  calorie_goal?: number
}

export function useProfile() {
  return useQuery<UserProfile>({
    queryKey: ['profile'],
    queryFn: async () => {
      const { data } = await api.get('/users/me/profile')
      return data
    },
  })
}

export function useCreateProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (profile: ProfileInput) => {
      const { data } = await api.post('/users/me/profile', profile)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

export function useUpdateProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (profile: Partial<ProfileInput>) => {
      const { data } = await api.patch('/users/me/profile', profile)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}
