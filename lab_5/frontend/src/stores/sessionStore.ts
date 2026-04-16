import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface LoggedSet {
  exercise_id: number
  set_number: number
  weight_kg: number | null
  reps: number
  rpe: number | null
}

interface ActiveSessionState {
  sessionId: number | null
  planDayId: number | null
  currentExerciseIndex: number
  loggedSets: LoggedSet[]
  timerStartedAt: number | null
  isActive: boolean

  startSession: (sessionId: number, planDayId: number | null) => void
  setExerciseIndex: (index: number) => void
  addSet: (set: LoggedSet) => void
  removeLastSet: (exerciseId: number) => void
  startTimer: () => void
  endSession: () => void
  reset: () => void
}

export const useSessionStore = create<ActiveSessionState>()(
  persist(
    (set) => ({
      sessionId: null,
      planDayId: null,
      currentExerciseIndex: 0,
      loggedSets: [],
      timerStartedAt: null,
      isActive: false,

      startSession: (sessionId, planDayId) =>
        set({
          sessionId,
          planDayId,
          currentExerciseIndex: 0,
          loggedSets: [],
          timerStartedAt: Date.now(),
          isActive: true,
        }),

      setExerciseIndex: (index) => set({ currentExerciseIndex: index }),

      addSet: (newSet) =>
        set((state) => ({ loggedSets: [...state.loggedSets, newSet] })),

      removeLastSet: (exerciseId) =>
        set((state) => {
          const sets = [...state.loggedSets]
          const lastIdx = sets.findLastIndex((s) => s.exercise_id === exerciseId)
          if (lastIdx !== -1) sets.splice(lastIdx, 1)
          return { loggedSets: sets }
        }),

      startTimer: () => set({ timerStartedAt: Date.now() }),

      endSession: () => set({ isActive: false }),

      reset: () =>
        set({
          sessionId: null,
          planDayId: null,
          currentExerciseIndex: 0,
          loggedSets: [],
          timerStartedAt: null,
          isActive: false,
        }),
    }),
    {
      name: 'active-session',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
)
