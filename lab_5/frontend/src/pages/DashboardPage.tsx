import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import StatsCard from '../components/common/StatsCard'
import EmptyState from '../components/common/EmptyState'
import { useTodayWorkout, useGenerateWorkout } from '../hooks/useWorkout'
import { useAnalyticsSummary } from '../hooks/useAnalytics'
import { formatDuration } from '../lib/formatters'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: todayWorkout, isLoading: todayLoading } = useTodayWorkout()
  const { data: summary } = useAnalyticsSummary()
  const generateWorkout = useGenerateWorkout()

  const handleGenerate = async () => {
    await generateWorkout.mutateAsync({})
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Welcome back! Here's your fitness overview.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard label="This Week" value={summary?.sessions_this_week ?? 0} icon="🏋️" />
        <StatsCard label="Total Sessions" value={summary?.total_sessions ?? 0} icon="📈" />
        <StatsCard
          label="Total Duration"
          value={formatDuration((summary?.total_duration_minutes ?? 0) * 60)}
          icon="⏱️"
        />
        <StatsCard
          label="Calories Burned"
          value={`${Math.round(summary?.total_calories ?? 0)}`}
          icon="🔥"
        />
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Today's Workout</h2>

        {todayLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        ) : todayWorkout ? (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-primary">{todayWorkout.focus}</h3>
                <p className="text-sm text-muted-foreground">
                  {todayWorkout.exercises.length} exercises
                </p>
              </div>
              <Button
                size="lg"
                className="font-semibold text-lg px-8"
                onClick={() => navigate(`/workout/${todayWorkout.id}`)}
              >
                Start Workout
              </Button>
            </div>

            <div className="space-y-2">
              {todayWorkout.exercises.map((ex) => (
                <div
                  key={ex.id}
                  className="flex items-center justify-between py-2.5 px-4 rounded-xl bg-muted"
                >
                  <span className="font-medium text-sm">{ex.exercise_name}</span>
                  <span className="text-xs text-muted-foreground">
                    {ex.sets} x {ex.reps_min}-{ex.reps_max}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <EmptyState
            icon="📋"
            title="No workout for today"
            description="Generate a personalized workout plan to get started!"
            actionLabel={generateWorkout.isPending ? 'Generating...' : 'Generate Plan'}
            onAction={handleGenerate}
          />
        )}
      </Card>
    </div>
  )
}
