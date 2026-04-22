import { useNavigate } from 'react-router-dom'
import { Loader2, Check, X, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import ActivityRing from '../components/common/ActivityRing'
import EmptyState from '../components/common/EmptyState'
import {
  useTodayWorkout,
  useGenerateWorkout,
  useWorkoutPlans,
  type PlanDay,
  type PlanDayStatus,
} from '../hooks/useWorkout'
import { useAnalyticsSummary } from '../hooks/useAnalytics'
import { useProfile } from '../hooks/useProfile'
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

  return (
    <div className="rounded-3xl p-5" style={{ background: '#1C1C1E' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-white">This Week</h2>
        <span className="text-xs" style={{ color: '#8E8E93' }}>
          {days.filter((d) => d.status === 'done').length} of{' '}
          {days.filter((d) => !d.is_rest).length} done
        </span>
      </div>
      <div className="grid grid-cols-7 gap-1.5">
        {Array.from({ length: 7 }, (_, i) => {
          const day = byDow.get(i)
          const status: PlanDayStatus = day?.status ?? 'upcoming'
          const isToday = i === TODAY_IDX
          const clickable = isToday && !day?.is_rest
          const isRest = day?.is_rest ?? false

          let bgColor = '#2C2C2E'
          let textColor = '#8E8E93'
          let borderColor = 'transparent'
          if (status === 'done') { bgColor = 'rgba(173,255,47,0.12)'; textColor = '#ADFF2F' }
          if (status === 'today') { bgColor = '#ADFF2F'; textColor = '#000' }
          if (isToday && status !== 'today') { borderColor = '#ADFF2F' }

          return (
            <button
              key={i}
              type="button"
              onClick={clickable ? onStartToday : undefined}
              disabled={!clickable}
              className="flex flex-col items-center gap-1 rounded-2xl py-2.5 px-0.5 transition-opacity"
              style={{ background: bgColor, border: `1.5px solid ${borderColor}`, cursor: clickable ? 'pointer' : 'default' }}
              title={`${DAY_NAMES_SHORT[i]} · ${status}`}
            >
              <span className="text-[9px] font-bold" style={{ color: textColor, opacity: 0.8 }}>
                {DAY_NAMES_SHORT[i]}
              </span>
              <StatusIcon status={status} textColor={textColor} />
              <span className="text-[8px] font-medium" style={{ color: textColor }}>
                {isRest ? 'Rest' : status === 'done' ? '✓' : ''}
              </span>
            </button>
          )
        })}
      </div>
      <p className="text-[10px] mt-3" style={{ color: '#8E8E93' }}>
        Plan #{planId} · tap today to start
      </p>
    </div>
  )
}

function StatusIcon({ status, textColor }: { status: PlanDayStatus; textColor: string }) {
  const style = { color: textColor }
  if (status === 'done') return <Check className="h-3.5 w-3.5" style={style} />
  if (status === 'skipped') return <X className="h-3.5 w-3.5" style={style} />
  if (status === 'today') return <Clock className="h-3.5 w-3.5" style={style} />
  return <span className="h-3.5 w-3.5 block" />
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: todayWorkout, isLoading: todayLoading } = useTodayWorkout()
  const { data: plans } = useWorkoutPlans()
  const { data: summary } = useAnalyticsSummary()
  const generateWorkout = useGenerateWorkout()

  const { data: profile } = useProfile()
  const activePlan = plans?.[0]
  const calorieGoal = profile?.calorie_goal ?? 500
  const calories = Math.round(summary?.total_calories ?? 0)
  const calorieProgress = Math.min(1, calories / calorieGoal)

  const startToday = () => {
    if (todayWorkout) {
      navigate(`/workout/${todayWorkout.plan_id}/${todayWorkout.day_of_week}`)
    }
  }

  const todayDone = todayWorkout?.status === 'done'

  const stats = [
    { label: 'This Week', value: summary?.sessions_this_week ?? 0, color: '#ADFF2F' },
    { label: 'Total Sessions', value: summary?.total_sessions ?? 0, color: '#BF5AF2' },
    { label: 'Duration', value: formatDuration((summary?.total_duration_minutes ?? 0) * 60), color: '#32D2FF' },
    { label: 'Calories', value: `${calories} kcal`, color: '#FF375F' },
  ]

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Summary</h1>
        <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>
          {new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'short' })}
        </p>
      </div>

      {/* Activity Ring Hero */}
      <div className="rounded-3xl p-5" style={{ background: '#1C1C1E' }}>
        <h2 className="text-sm font-semibold text-white mb-4">Activity Ring</h2>
        <div className="flex items-center gap-6">
          <ActivityRing progress={calorieProgress} color="#FF375F" size={160} strokeWidth={20}>
            <div className="text-center">
              <span className="text-2xl font-bold text-white">{Math.round(calorieProgress * 100)}%</span>
            </div>
          </ActivityRing>
          <div className="flex flex-col gap-3">
            <div>
              <p className="text-xs font-semibold mb-0.5" style={{ color: '#8E8E93' }}>MOVE</p>
              <p className="text-xl font-bold" style={{ color: '#FF375F' }}>
                {calories}<span className="text-sm font-medium ml-1" style={{ color: '#8E8E93' }}>/{calorieGoal} KCAL</span>
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold mb-0.5" style={{ color: '#8E8E93' }}>SESSIONS</p>
              <p className="text-xl font-bold" style={{ color: '#ADFF2F' }}>
                {summary?.sessions_this_week ?? 0}
                <span className="text-sm font-medium ml-1" style={{ color: '#8E8E93' }}>this week</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="rounded-2xl p-4" style={{ background: '#1C1C1E' }}>
            <p className="text-[11px] font-semibold uppercase tracking-wide mb-1" style={{ color: '#8E8E93' }}>
              {s.label}
            </p>
            <p className="text-xl font-bold" style={{ color: s.color }}>
              {s.value}
            </p>
          </div>
        ))}
      </div>

      {/* Weekly strip */}
      {activePlan && activePlan.days.length > 0 && (
        <WeeklyStrip days={activePlan.days} planId={activePlan.id} onStartToday={startToday} />
      )}

      {/* Today's Workout */}
      <div className="rounded-3xl p-5" style={{ background: '#1C1C1E' }}>
        <h2 className="text-base font-semibold text-white mb-4">Today's Workout</h2>

        {todayLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" style={{ color: '#ADFF2F' }} />
          </div>
        ) : todayWorkout ? (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold" style={{ color: '#ADFF2F' }}>{todayWorkout.focus}</h3>
                <p className="text-sm" style={{ color: '#8E8E93' }}>
                  {todayWorkout.exercises.length} exercises{todayDone ? ' · completed' : ''}
                </p>
              </div>
              <Button
                size="lg"
                className="font-bold px-6 rounded-full text-black"
                style={{ background: '#ADFF2F', color: '#000' }}
                onClick={startToday}
                disabled={todayDone}
              >
                {todayDone ? 'Done ✓' : 'Start'}
              </Button>
            </div>

            <div className="space-y-2">
              {todayWorkout.exercises.map((ex) => (
                <div
                  key={ex.id}
                  className="flex items-center justify-between py-2.5 px-4 rounded-2xl"
                  style={{ background: '#2C2C2E' }}
                >
                  <p className="font-medium text-sm text-white">{ex.exercise_name}</p>
                  <span className="text-xs font-semibold" style={{ color: '#8E8E93' }}>
                    {ex.sets} × {ex.reps_min}–{ex.reps_max}
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
            actionLabel={generateWorkout.isPending ? 'Generating…' : 'Generate Plan'}
            onAction={() => generateWorkout.mutateAsync({})}
          />
        )}
      </div>
    </div>
  )
}
