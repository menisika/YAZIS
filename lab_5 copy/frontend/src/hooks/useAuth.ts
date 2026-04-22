import { useEffect } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../config/firebase'
import { useAuthStore } from '../stores/authStore'
import api from '../config/api'

export function useAuth() {
  const { user, token, isLoading, setUser, setToken, setLoading } = useAuthStore()

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const idToken = await firebaseUser.getIdToken()
          setToken(idToken)

          const { data } = await api.post('/auth/verify-token', { token: idToken })
          setUser(data)
        } catch {
          setUser(null)
          setToken(null)
        }
      } else {
        setUser(null)
        setToken(null)
      }
      setLoading(false)
    })

    return unsubscribe
  }, [setUser, setToken, setLoading])

  return { user, token, isLoading }
}
