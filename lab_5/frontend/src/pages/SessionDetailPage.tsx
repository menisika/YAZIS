import { useParams, useNavigate } from 'react-router-dom'
import { Loader2, ChevronLeft, Clock, Flame, Dumbbell } from 'lucide-react'
import { useSessionDetail } from '../hooks/useSession'
import { formatDate, formatDuration } from '../lib/formatters'

export default function SessionDetailPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const { data: session, isLoading } = useSessionDetail(sessionId ? Number(sessionId) : null)

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#ADFF2F' }} />
      </div>
    )
  }

  if (!session) {
    return <div className="text-center py-12" style={{ color: '#8E8E93' }}>Session not found</div>
  }

  const exerciseGroups = session.sets.reduce(
    (acc, set) => {
      const key = set.exercise_id
      if (!acc[key]) acc[key] = []
      acc[key].push(set)
      return acc
    },
    {} as Record<number, typeof session.sets>
  )

  const stats = [
    {
      label: 'Duration',
      value: session.duration_seconds ? formatDuration(session.duration_seconds) : '--',
      icon: Clock,
      color: '#32D2FF',
    },
    {
      label: 'Sets',
      value: session.sets.length,
      icon: Dumbbell,
      color: '#BF5AF2',
    },
    {
      label: 'Calories',
      value: session.estimated_calories ? Math.round(session.estimated_calories) : '--',
      icon: Flame,
      color: '#FF375F',
    },
  ]

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => navigate('/history')}
          className="flex items-center justify-center w-9 h-9 rounded-full"
          style={{ background: '#1C1C1E' }}
        >
          <ChevronLeft className="h-5 w-5 text-white" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Session</h1>
          <p className="text-sm" style={{ color: '#8E8E93' }}>{formatDate(session.started_at)}</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="rounded-2xl p-4 text-center" style={{ background: '#1C1C1E' }}>
            <s.icon className="h-5 w-5 mx-auto mb-1" style={{ color: s.color }} />
            <p className="text-lg font-bold text-white">{s.value}</p>
            <p className="text-[10px] uppercase font-semibold mt-0.5" style={{ color: '#8E8E93' }}>{s.label}</p>
          </div>
        ))}
      </div>

      {/* Exercise groups */}
      <div className="space-y-3">
        {Object.entries(exerciseGroups).map(([exerciseId, sets]) => (
          <div
            key={exerciseId}
            className="rounded-3xl p-5"
            style={{ background: '#1C1C1E' }}
          >
            <h3 className="font-bold text-white mb-3">
              {sets[0]?.exercise_name ?? `Exercise #${exerciseId}`}
            </h3>
            <div className="space-y-2">
              {sets.map((set, i) => (
                <div
                  key={set.id}
                  className="flex justify-between items-center px-3 py-2 rounded-xl text-sm"
                  style={{ background: i % 2 === 0 ? '#2C2C2E' : 'transparent' }}
                >
                  <span style={{ color: '#8E8E93' }}>Set {set.set_number}</span>
                  <span className="font-semibold text-white">
                    {set.weight_kg ?? 'BW'} kg × {set.reps} reps
                    {set.rpe ? (
                      <span className="ml-2 text-xs font-medium" style={{ color: '#BF5AF2' }}>
                        RPE {set.rpe}
                      </span>
                    ) : null}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
