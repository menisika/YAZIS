import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import ProtectedRoute from './components/layout/ProtectedRoute'
import AppShell from './components/layout/AppShell'

import LoginPage from './pages/LoginPage'
import OnboardingPage from './pages/OnboardingPage'
import DashboardPage from './pages/DashboardPage'
import WorkoutPlanPage from './pages/WorkoutPlanPage'
import ActiveWorkoutPage from './pages/ActiveWorkoutPage'
import HistoryPage from './pages/HistoryPage'
import SessionDetailPage from './pages/SessionDetailPage'
import AnalyticsPage from './pages/AnalyticsPage'
import ExerciseLibraryPage from './pages/ExerciseLibraryPage'
import ProfilePage from './pages/ProfilePage'
import AssistantPage from './pages/AssistantPage'

export default function App() {
  useAuth()

  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <OnboardingPage />
            </ProtectedRoute>
          }
        />
        <Route
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/plan" element={<WorkoutPlanPage />} />
          <Route path="/workout/:planId/:dayOfWeek" element={<ActiveWorkoutPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/history/:sessionId" element={<SessionDetailPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/exercises" element={<ExerciseLibraryPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/assistant" element={<AssistantPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
