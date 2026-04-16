import { useParams } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useSessionDetail } from '../hooks/useSession'
import { formatDate, formatDuration } from '../lib/formatters'

export default function SessionDetailPage() {
  const { sessionId } = useParams()
  const { data: session, isLoading } = useSessionDetail(sessionId ? Number(sessionId) : null)

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!session) {
    return <div className="text-center py-12 text-muted-foreground">Session not found</div>
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Session Detail</h1>
        <p className="text-muted-foreground">{formatDate(session.started_at)}</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card className="p-4 text-center">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Duration</p>
          <p className="text-lg font-bold mt-1">
            {session.duration_seconds ? formatDuration(session.duration_seconds) : '--'}
          </p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Sets</p>
          <p className="text-lg font-bold mt-1">{session.sets.length}</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Calories</p>
          <p className="text-lg font-bold mt-1">
            {session.estimated_calories ? Math.round(session.estimated_calories) : '--'}
          </p>
        </Card>
      </div>

      <div className="space-y-4">
        {Object.entries(exerciseGroups).map(([exerciseId, sets]) => (
          <Card key={exerciseId} className="p-5">
            <h3 className="font-semibold mb-3">
              {sets[0]?.exercise_name ?? `Exercise #${exerciseId}`}
            </h3>
            <div className="space-y-1">
              {sets.map((set, i) => (
                <div key={set.id}>
                  <div className="flex justify-between text-sm py-1.5">
                    <span className="text-muted-foreground">Set {set.set_number}</span>
                    <span className="font-medium">
                      {set.weight_kg ?? 'BW'} kg x {set.reps} reps
                      {set.rpe ? ` @ RPE ${set.rpe}` : ''}
                    </span>
                  </div>
                  {i < sets.length - 1 && <Separator />}
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
