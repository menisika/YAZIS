import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, MoreVertical } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import EmptyState from '../components/common/EmptyState'
import { useWorkoutPlans, useGenerateWorkout, useSwapDays, useToggleRest } from '../hooks/useWorkout'
import { DAY_NAMES, DAY_NAMES_SHORT } from '../lib/formatters'

export default function WorkoutPlanPage() {
  const navigate = useNavigate()
  const { data: plans, isLoading } = useWorkoutPlans()
  const generateWorkout = useGenerateWorkout()
  const swapDays = useSwapDays()
  const toggleRest = useToggleRest()

  const [openMenu, setOpenMenu] = useState<number | null>(null)
  const [swapFrom, setSwapFrom] = useState<number | null>(null)

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

  const handleToggleRest = async (dow: number) => {
    setOpenMenu(null)
    await toggleRest.mutateAsync(dow)
  }

  const handleSwapConfirm = async (targetDow: number) => {
    if (swapFrom === null) return
    setSwapFrom(null)
    await swapDays.mutateAsync({ day_a: swapFrom, day_b: targetDow })
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
          const isRest = day?.is_rest ?? true
          const isBusy = swapDays.isPending || toggleRest.isPending

          return (
            <Card key={i} className={`p-5 relative ${!isRest ? 'border-l-4 border-l-primary' : 'opacity-80'}`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold">{DAY_NAMES_SHORT[i]}</h3>
                <div className="flex items-center gap-1">
                  {day && (
                    <span className="text-xs bg-primary/10 text-primary px-2.5 py-1 rounded-full font-medium">
                      {day.focus}
                    </span>
                  )}
                  {/* Day actions menu */}
                  <div className="relative">
                    <button
                      className="p-1 rounded hover:bg-muted transition-colors"
                      onClick={() => setOpenMenu(openMenu === i ? null : i)}
                      disabled={isBusy}
                    >
                      <MoreVertical className="h-4 w-4 text-muted-foreground" />
                    </button>
                    {openMenu === i && (
                      <div className="absolute right-0 top-7 z-20 bg-card border border-border rounded-xl shadow-lg min-w-[160px] py-1">
                        <button
                          className="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors"
                          onClick={() => handleToggleRest(i)}
                        >
                          {isRest ? 'Make workout day' : 'Make rest day'}
                        </button>
                        <button
                          className="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors"
                          onClick={() => { setSwapFrom(i); setOpenMenu(null) }}
                        >
                          Swap with…
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {day && !isRest ? (
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
                    onClick={() => navigate(`/workout/${activePlan.id}/${i}`)}
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

      {/* Click-outside to close menu */}
      {openMenu !== null && (
        <div className="fixed inset-0 z-10" onClick={() => setOpenMenu(null)} />
      )}

      {/* Swap day picker dialog */}
      <Dialog open={swapFrom !== null} onOpenChange={(open) => !open && setSwapFrom(null)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Swap {swapFrom !== null ? DAY_NAMES[swapFrom] : ''} with…</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {Array.from({ length: 7 }, (_, i) => {
              if (i === swapFrom) return null
              return (
                <Button
                  key={i}
                  variant="outline"
                  onClick={() => handleSwapConfirm(i)}
                  disabled={swapDays.isPending}
                >
                  {DAY_NAMES[i]}
                </Button>
              )
            })}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
