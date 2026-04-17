import { useNavigate } from 'react-router-dom'
import { Loader2, Check, X, Clock } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import StatsCard from '../components/common/StatsCard'
import EmptyState from '../components/common/EmptyState'
import {
  useTodayWorkout,
  useGenerateWorkout,
  useWorkoutPlans,
  type PlanDay,
  type PlanDayStatus,
} from '../hooks/useWorkout'
import { useAnalyticsSummary } from '../hooks/useAnalytics'
import { formatDuration, DAY_NAMES_SHORT } from '../lib/formatters'

const TODAY_IDX = (new Date().getDay() + 6) % 7

function WeeklyStrip({
  days,
  planId,
  onStartToday,
}: {
  days: PlanDay[]
  planId: number
  onStartToday: () => void
}) {
  const byDow = new Map(days.map((d) => [d.day_of_week, d]))

  const statusStyles: Record<PlanDayStatus, string> = {
    done: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
    skipped: 'bg-muted-foreground/10 text-muted-foreground border-muted-foreground/20',
    today: 'bg-primary text-primary-foreground border-primary',
    upcoming: 'bg-muted text-muted-foreground border-border',
    rest: 'bg-muted/60 text-muted-foreground border-border',
  }

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">This Week</h2>
        <span className="text-xs text-muted-foreground">
          {days.filter((d) => d.status === 'done').length} of{' '}
          {days.filter((d) => !d.is_rest).length} done
        </span>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {Array.from({ length: 7 }, (_, i) => {
          const day = byDow.get(i)
          const status: PlanDayStatus = day?.status ?? 'upcoming'
          const label = day?.focus && !day.is_rest ? day.focus : day?.is_rest ? 'Rest' : '—'
          const isToday = i === TODAY_IDX
          const clickable = isToday && !day?.is_rest
          return (
            <button
              key={i}
              type="button"
              onClick={clickable ? onStartToday : undefined}
              disabled={!clickable}
              className={`flex flex-col items-center gap-1 rounded-xl border px-1 py-2 transition-opacity ${statusStyles[status]} ${
                clickable ? 'cursor-pointer hover:opacity-90' : 'cursor-default'
              }`}
              title={`${DAY_NAMES_SHORT[i]} · ${status}`}
            >
              <span className="text-[10px] font-semibold opacity-80">{DAY_NAMES_SHORT[i]}</span>
              <StatusIcon status={status} />
              <span className="text-[10px] truncate max-w-full px-1">{label}</span>
            </button>
          )
        })}
      </div>
      <p className="text-[11px] text-muted-foreground mt-3">
        Plan #{planId} · green = done, gray = skipped, filled = today.
      </p>
    </Card>
  )
}

function StatusIcon({ status }: { status: PlanDayStatus }) {
  if (status === 'done') return <Check className="h-4 w-4" />
  if (status === 'skipped') return <X className="h-4 w-4" />
  if (status === 'today') return <Clock className="h-4 w-4" />
  return <span className="h-4 w-4 block" />
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: todayWorkout, isLoading: todayLoading } = useTodayWorkout()
  const { data: plans } = useWorkoutPlans()
  const { data: summary } = useAnalyticsSummary()
  const generateWorkout = useGenerateWorkout()

  const activePlan = plans?.[0]

  const handleGenerate = async () => {
    await generateWorkout.mutateAsync({})
  }

  const startToday = () => {
    if (todayWorkout) {
      navigate(`/workout/${todayWorkout.plan_id}/${todayWorkout.day_of_week}`)
    }
  }

  const todayDone = todayWorkout?.status === 'done'

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

      {activePlan && activePlan.days.length > 0 && (
        <WeeklyStrip days={activePlan.days} planId={activePlan.id} onStartToday={startToday} />
      )}

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
                  {todayDone && ' · completed'}
                </p>
              </div>
              <Button
                size="lg"
                className="font-semibold text-lg px-8"
                onClick={startToday}
                disabled={todayDone}
              >
                {todayDone ? 'Completed' : 'Start Workout'}
              </Button>
            </div>

            <div className="space-y-2">
              {todayWorkout.exercises.map((ex) => (
                <div
                  key={ex.id}
                  className="flex items-center justify-between py-2.5 px-4 rounded-xl bg-muted"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-sm">{ex.exercise_name}</p>
                    {ex.exercise_description && (
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                        {ex.exercise_description}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">
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
