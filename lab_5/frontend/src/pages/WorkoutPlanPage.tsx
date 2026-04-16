import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import EmptyState from '../components/common/EmptyState'
import { useWorkoutPlans, useGenerateWorkout } from '../hooks/useWorkout'
import { DAY_NAMES_SHORT } from '../lib/formatters'

export default function WorkoutPlanPage() {
  const navigate = useNavigate()
  const { data: plans, isLoading } = useWorkoutPlans()
  const generateWorkout = useGenerateWorkout()

  const activePlan = plans?.[0]

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!activePlan) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Workout Plan</h1>
        <EmptyState
          icon="📋"
          title="No workout plan yet"
          description="Let AI create a personalized weekly plan based on your profile and goals."
          actionLabel={generateWorkout.isPending ? 'Generating...' : 'Generate My Plan'}
          onAction={() => generateWorkout.mutateAsync({})}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Workout Plan</h1>
          <p className="text-muted-foreground text-sm">{activePlan.name}</p>
        </div>
        <Button
          variant="outline"
          disabled={generateWorkout.isPending}
          onClick={() => generateWorkout.mutateAsync({})}
        >
          {generateWorkout.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
          Regenerate
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Array.from({ length: 7 }, (_, i) => {
          const day = activePlan.days.find((d) => d.day_of_week === i)
          return (
            <Card key={i} className={`p-5 ${day ? 'border-l-4 border-l-primary' : 'opacity-60'}`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold">{DAY_NAMES_SHORT[i]}</h3>
                {day && (
                  <span className="text-xs bg-primary/10 text-primary px-2.5 py-1 rounded-full font-medium">
                    {day.focus}
                  </span>
                )}
              </div>

              {day ? (
                <div className="space-y-2">
                  {day.exercises.map((ex) => (
                    <div key={ex.id} className="text-xs text-muted-foreground flex justify-between">
                      <span className="truncate mr-2">{ex.exercise_name}</span>
                      <span className="whitespace-nowrap font-medium">
                        {ex.sets}x{ex.reps_min}-{ex.reps_max}
                      </span>
                    </div>
                  ))}
                  <Button
                    size="sm"
                    variant="secondary"
                    className="w-full mt-3"
                    onClick={() => navigate(`/workout/${day.id}`)}
                  >
                    Start
                  </Button>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">Rest Day</p>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
