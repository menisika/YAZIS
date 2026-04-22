import { useNavigate } from 'react-router-dom'
import { Loader2, ChevronRight, Clock, Flame, Dumbbell } from 'lucide-react'
import EmptyState from '../components/common/EmptyState'
import { useSessions } from '../hooks/useSession'
import { formatDate, formatDuration } from '../lib/formatters'

export default function HistoryPage() {
  const navigate = useNavigate()
  const { data: sessions, isLoading } = useSessions()

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#ADFF2F' }} />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold text-white tracking-tight">History</h1>

      {!sessions?.length ? (
        <EmptyState
          icon="📜"
          title="No workouts yet"
          description="Complete your first workout to see it here."
        />
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <button
              key={session.id}
              type="button"
              onClick={() => navigate(`/history/${session.id}`)}
              className="w-full text-left rounded-3xl p-5 transition-all"
              style={{ background: '#1C1C1E', border: '1px solid rgba(255,255,255,0.05)' }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(173,255,47,0.2)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)')}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-white">{formatDate(session.started_at)}</p>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="flex items-center gap-1 text-xs" style={{ color: '#8E8E93' }}>
                      <Dumbbell className="h-3.5 w-3.5" style={{ color: '#BF5AF2' }} />
                      {session.sets.length} sets
                    </span>
                    {session.duration_seconds ? (
                      <span className="flex items-center gap-1 text-xs" style={{ color: '#8E8E93' }}>
                        <Clock className="h-3.5 w-3.5" style={{ color: '#32D2FF' }} />
                        {formatDuration(session.duration_seconds)}
                      </span>
                    ) : null}
                    {session.estimated_calories ? (
                      <span className="flex items-center gap-1 text-xs" style={{ color: '#8E8E93' }}>
                        <Flame className="h-3.5 w-3.5" style={{ color: '#FF375F' }} />
                        {Math.round(session.estimated_calories)} cal
                      </span>
                    ) : null}
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 shrink-0 ml-3" style={{ color: '#8E8E93' }} />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
