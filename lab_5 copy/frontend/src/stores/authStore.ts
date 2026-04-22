import { create } from 'zustand'
import { signOut as firebaseSignOut } from 'firebase/auth'
import { auth } from '../config/firebase'

interface User {
  id: number
  firebase_uid: string
  email: string
  display_name: string | null
  has_profile: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
  signOut: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setLoading: (isLoading) => set({ isLoading }),
  signOut: async () => {
    await firebaseSignOut(auth)
    set({ user: null, token: null })
  },
}))
