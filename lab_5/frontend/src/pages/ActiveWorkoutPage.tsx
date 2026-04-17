import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Loader2, Pause, Play, ChevronLeft, ChevronRight, Video, Flag } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { useSessionStore } from '../stores/sessionStore'
import { useStartSession, useLogSet, useEndSession } from '../hooks/useSession'
import { useStopwatch, useCountdown, formatTime } from '../hooks/useTimer'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ExerciseVideoPlayer from '../components/common/ExerciseVideoPlayer'
import api from '../config/api'
import type { PlanDay } from '../hooks/useWorkout'

const TODAY_IDX = (new Date().getDay() + 6) % 7

export default function ActiveWorkoutPage() {
  const { planId, dayOfWeek } = useParams()
  const navigate = useNavigate()
  const isToday = Number(dayOfWeek) === TODAY_IDX
  const [planDay, setPlanDay] = useState<PlanDay | null>(null)
  const [loading, setLoading] = useState(true)
  const [showVideo, setShowVideo] = useState(false)

  const store = useSessionStore()
  const startSession = useStartSession()
  const logSet = useLogSet()
  const endSession = useEndSession()
  const stopwatch = useStopwatch()
  const restTimer = useCountdown(90)

  const [weight, setWeight] = useState('')
  const [reps, setReps] = useState('')
  const [rpe, setRpe] = useState('')
  const [showRestTimer, setShowRestTimer] = useState(false)
  const [showEndConfirm, setShowEndConfirm] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const { data: plans } = await api.get('/workouts')
        for (const plan of plans) {
          if (plan.id === Number(planId)) {
            const day = plan.days?.find((d: PlanDay) => d.day_of_week === Number(dayOfWeek))
            if (day) setPlanDay(day)
            break
          }
        }
      } catch {
        console.error('Failed to load workout')
      }
      setLoading(false)
    }
    load()
  }, [planId, dayOfWeek])

  const handleStart = async () => {
    const result = await startSession.mutateAsync({
      plan_id: Number(planId),
      plan_day_of_week: Number(dayOfWeek),
    })
    store.startSession(result.id, Number(dayOfWeek))
    stopwatch.start()
  }

  const currentExercise = planDay?.exercises[store.currentExerciseIndex]
  const setsForCurrent = store.loggedSets.filter(
    (s) => s.exercise_id === currentExercise?.exercise_id
  )

  const handleLogSet = async () => {
    if (!store.sessionId || !currentExercise) return
    const setData = {
      sessionId: store.sessionId,
      exercise_id: currentExercise.exercise_id,
      set_number: setsForCurrent.length + 1,
      weight_kg: weight ? Number(weight) : null,
      reps: Number(reps) || 0,
      rpe: rpe ? Number(rpe) : null,
    }
    await logSet.mutateAsync(setData)
    store.addSet({
      exercise_id: currentExercise.exercise_id,
      set_number: setsForCurrent.length + 1,
      weight_kg: weight ? Number(weight) : null,
      reps: Number(reps) || 0,
      rpe: rpe ? Number(rpe) : null,
    })
    setReps('')
    setShowRestTimer(true)
    restTimer.reset(currentExercise.rest_seconds)
    restTimer.start()
  }

  const handleEndWorkout = async () => {
    if (!store.sessionId) return
    await endSession.mutateAsync({ sessionId: store.sessionId, status: 'completed' })
    store.reset()
    stopwatch.reset()
    navigate('/history')
  }

  if (loading) return <LoadingSpinner label="Loading workout..." />

  if (!planDay) {
    return <div className="text-center py-12 text-muted-foreground">Workout not found</div>
  }

  if (!store.isActive) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
        <h1 className="text-3xl font-bold text-primary">{planDay.focus}</h1>
        <p className="text-muted-foreground">{planDay.exercises.length} exercises</p>
        <Button
          size="lg"
          className="text-xl px-12 py-8 font-bold"
          onClick={handleStart}
          disabled={startSession.isPending || !isToday}
        >
          {startSession.isPending && <Loader2 className="h-5 w-5 animate-spin mr-2" />}
          START WORKOUT
        </Button>
        {!isToday && (
          <p className="text-sm text-muted-foreground">
            Only today's workout can be started.
          </p>
        )}
      </div>
    )
  }

  const isLastExercise =
    planDay.exercises.length > 0 &&
    store.currentExerciseIndex === planDay.exercises.length - 1

  return (
    <div className="space-y-6">
      {/* Timer Bar */}
      <div className="flex items-center justify-between bg-card rounded-xl p-4 border border-border sticky top-0 z-10 shadow-sm">
        <div className="text-3xl font-mono font-bold text-primary">
          {formatTime(stopwatch.elapsed)}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={stopwatch.isRunning ? stopwatch.pause : stopwatch.start}>
            {stopwatch.isRunning ? <Pause className="h-4 w-4 mr-1" /> : <Play className="h-4 w-4 mr-1" />}
            {stopwatch.isRunning ? 'Pause' : 'Resume'}
          </Button>
          <Button variant="destructive" size="sm" onClick={() => setShowEndConfirm(true)}>
            End Workout
          </Button>
        </div>
      </div>

      {/* Exercise Progress */}
      <Progress value={((store.currentExerciseIndex + 1) / planDay.exercises.length) * 100} />

      {/* Current Exercise */}
      {currentExercise && (
        <Card className="p-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold">{currentExercise.exercise_name}</h2>
            <p className="text-muted-foreground">
              Target: {currentExercise.sets} sets x {currentExercise.reps_min}-{currentExercise.reps_max} reps
            </p>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2"
              onClick={() => setShowVideo(!showVideo)}
            >
              <Video className="h-4 w-4 mr-1" />
              {showVideo ? 'Hide Tutorial' : 'Watch Tutorial'}
            </Button>
          </div>

          {showVideo && (
            <div className="mb-6">
              <ExerciseVideoPlayer exerciseId={currentExercise.exercise_id} />
            </div>
          )}

          {/* Logged sets */}
          {setsForCurrent.length > 0 && (
            <div className="mb-4 space-y-2">
              {setsForCurrent.map((s, i) => (
                <div key={i} className="flex justify-between bg-accent/10 rounded-xl px-4 py-2.5 text-sm">
                  <span className="text-muted-foreground">Set {s.set_number}</span>
                  <span className="font-medium">{s.weight_kg ?? 'BW'} kg x {s.reps} reps</span>
                </div>
              ))}
            </div>
          )}

          {/* Input row */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="space-y-1.5">
              <Label htmlFor="aw-weight" className="text-xs">Weight (kg)</Label>
              <Input id="aw-weight" type="number" value={weight} onChange={(e) => setWeight(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="aw-reps" className="text-xs">Reps</Label>
              <Input id="aw-reps" type="number" value={reps} onChange={(e) => setReps(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="aw-rpe" className="text-xs">RPE (1-10)</Label>
              <Input id="aw-rpe" type="number" value={rpe} onChange={(e) => setRpe(e.target.value)} />
            </div>
          </div>

          <Button
            size="lg"
            className="w-full text-lg font-semibold"
            onClick={handleLogSet}
            disabled={!reps || logSet.isPending}
          >
            {logSet.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
            Log Set {setsForCurrent.length + 1}
          </Button>

          {/* Navigation */}
          <div className="flex justify-between mt-4">
            <Button
              variant="outline"
              disabled={store.currentExerciseIndex === 0}
              onClick={() => store.setExerciseIndex(store.currentExerciseIndex - 1)}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            {isLastExercise ? (
              <Button
                variant="destructive"
                onClick={() => setShowEndConfirm(true)}
              >
                <Flag className="h-4 w-4 mr-1" />
                End Workout
              </Button>
            ) : (
              <Button
                variant="outline"
                onClick={() => {
                  store.setExerciseIndex(store.currentExerciseIndex + 1)
                  setWeight('')
                  setReps('')
                  setRpe('')
                  setShowVideo(false)
                }}
              >
                Next Exercise
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            )}
          </div>
        </Card>
      )}

      {/* Rest Timer Dialog */}
      <Dialog open={showRestTimer} onOpenChange={setShowRestTimer}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Rest Timer</DialogTitle>
            <DialogDescription>Take a break before your next set</DialogDescription>
          </DialogHeader>
          <div className="text-center">
            <div className="text-6xl font-mono font-bold text-primary my-8">
              {formatTime(restTimer.remaining)}
            </div>
            <div className="flex gap-3 justify-center">
              <Button variant="outline" size="sm" onClick={() => restTimer.reset(30)}>30s</Button>
              <Button variant="outline" size="sm" onClick={() => restTimer.reset(60)}>60s</Button>
              <Button variant="outline" size="sm" onClick={() => restTimer.reset(90)}>90s</Button>
              <Button variant="outline" size="sm" onClick={() => restTimer.reset(120)}>120s</Button>
            </div>
            <Button className="mt-4" onClick={() => setShowRestTimer(false)}>
              Skip Rest
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* End Confirmation Dialog */}
      <Dialog open={showEndConfirm} onOpenChange={setShowEndConfirm}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>End Workout?</DialogTitle>
            <DialogDescription>
              You've logged {store.loggedSets.length} sets. End this workout?
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => setShowEndConfirm(false)}>
              Continue
            </Button>
            <Button variant="destructive" onClick={handleEndWorkout} disabled={endSession.isPending}>
              {endSession.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              End Workout
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
