import { useNavigate } from 'react-router-dom'
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth'
import { auth } from '../config/firebase'
import { useAuthStore } from '../stores/authStore'
import { useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dumbbell } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()

  useEffect(() => {
    if (user) {
      navigate(user.has_profile ? '/' : '/onboarding', { replace: true })
    }
  }, [user, navigate])

  const handleGoogleSignIn = async () => {
    try {
      const provider = new GoogleAuthProvider()
      await signInWithPopup(auth, provider)
    } catch (err) {
      console.error('Sign-in error:', err)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 to-accent/5 p-4">
      <Card className="w-full max-w-md p-8 text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4">
            <Dumbbell className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold text-primary mb-2">FitPlanner AI</h1>
          <p className="text-muted-foreground">Your AI-powered adaptive fitness companion</p>
        </div>

        <Button size="lg" className="w-full" onClick={handleGoogleSignIn}>
          Sign in with Google
        </Button>

        <p className="text-xs text-muted-foreground mt-8">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>
      </Card>
    </div>
  )
}
