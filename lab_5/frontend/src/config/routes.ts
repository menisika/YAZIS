export const ROUTES = {
  LOGIN: '/login',
  ONBOARDING: '/onboarding',
  DASHBOARD: '/',
  WORKOUT_PLAN: '/plan',
  ACTIVE_WORKOUT: '/workout/:planId/:dayOfWeek',
  ASSISTANT: '/assistant',
  HISTORY: '/history',
  SESSION_DETAIL: '/history/:sessionId',
  ANALYTICS: '/analytics',
  EXERCISES: '/exercises',
  PROFILE: '/profile',
} as const
