import { useNavigate } from 'react-router-dom'
import { Loader2, ChevronRight } from 'lucide-react'
import { Card } from '@/components/ui/card'
import EmptyState from '../components/common/EmptyState'
import { useSessions } from '../hooks/useSession'
import { formatDate, formatDuration } from '../lib/formatters'

export default function HistoryPage() {
  const navigate = useNavigate()
  const { data: sessions, isLoading } = useSessions()

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Workout History</h1>

      {!sessions?.length ? (
        <EmptyState
          icon="📜"
          title="No workouts yet"
          description="Complete your first workout to see it here."
        />
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <Card
              key={session.id}
              className="p-4 cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate(`/history/${session.id}`)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{formatDate(session.started_at)}</p>
                  <p className="text-sm text-muted-foreground">
                    {session.sets.length} sets logged
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-sm font-medium">
                      {session.duration_seconds ? formatDuration(session.duration_seconds) : '--'}
                    </p>
                    {session.estimated_calories && (
                      <p className="text-xs text-muted-foreground">
                        {Math.round(session.estimated_calories)} cal
                      </p>
                    )}
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
