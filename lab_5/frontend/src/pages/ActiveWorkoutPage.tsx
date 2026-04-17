import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Loader2, Pause, Play, ChevronLeft, ChevronRight, Video, Flag, Dumbbell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import ActivityRing from '../components/common/ActivityRing'
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
  const [restTotal, setRestTotal] = useState(90)

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
    const rest = currentExercise.rest_seconds ?? 90
    setRestTotal(rest)
    restTimer.reset(rest)
    restTimer.start()
    setShowRestTimer(true)
  }

  const handleEndWorkout = async () => {
    if (!store.sessionId) return
    await endSession.mutateAsync({ sessionId: store.sessionId, status: 'completed' })
    store.reset()
    stopwatch.reset()
    navigate('/history')
  }

  if (loading) return <LoadingSpinner label="Loading workout…" />

  if (!planDay) {
    return <div className="text-center py-12" style={{ color: '#8E8E93' }}>Workout not found</div>
  }

  /* ── Pre-start screen ── */
  if (!store.isActive) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] gap-8 bg-black">
        <div className="text-center">
          <p className="text-sm font-semibold mb-1" style={{ color: '#8E8E93' }}>
            {planDay.exercises.length} exercises
          </p>
        </div>

        <ActivityRing progress={0} color="#ADFF2F" size={260} strokeWidth={24}>
          <div
            className="flex items-center justify-center w-16 h-16 rounded-full"
            style={{ background: 'rgba(173,255,47,0.12)' }}
          >
            <Dumbbell className="h-8 w-8" style={{ color: '#ADFF2F' }} />
          </div>
        </ActivityRing>

        <h1 className="text-3xl font-bold text-white text-center">{planDay.focus}</h1>

        <button
          type="button"
          onClick={handleStart}
          disabled={startSession.isPending || !isToday}
          className="flex items-center gap-3 px-10 py-4 rounded-full text-xl font-bold transition-all"
          style={{
            background: isToday ? '#ADFF2F' : '#2C2C2E',
            color: isToday ? '#000' : '#8E8E93',
            cursor: isToday ? 'pointer' : 'not-allowed',
          }}
        >
          {startSession.isPending && <Loader2 className="h-5 w-5 animate-spin" />}
          START WORKOUT
        </button>

        {!isToday && (
          <p className="text-sm" style={{ color: '#8E8E93' }}>Only today's workout can be started.</p>
        )}
      </div>
    )
  }

  const isLastExercise =
    planDay.exercises.length > 0 && store.currentExerciseIndex === planDay.exercises.length - 1

  const setProgress = currentExercise
    ? setsForCurrent.length / (currentExercise.sets || 1)
    : 0
  const exerciseProgress = (store.currentExerciseIndex + 1) / planDay.exercises.length

  return (
    <div className="min-h-screen bg-black pb-40">
      {/* Main content */}
      <div className="px-4 pt-4 space-y-6">
        {/* Exercise name + progress */}
        {currentExercise && (
          <>
            <div className="text-center space-y-1">
              <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#8E8E93' }}>
                Exercise {store.currentExerciseIndex + 1} of {planDay.exercises.length}
              </p>
              <h2 className="text-2xl font-bold text-white">{currentExercise.exercise_name}</h2>
              <p className="text-sm" style={{ color: '#8E8E93' }}>
                Target: {currentExercise.sets} sets × {currentExercise.reps_min}–{currentExercise.reps_max} reps
              </p>
              <button
                type="button"
                onClick={() => setShowVideo(!showVideo)}
                className="text-xs font-semibold px-3 py-1 rounded-full mt-1"
                style={{ background: 'rgba(50,210,255,0.12)', color: '#32D2FF' }}
              >
                <Video className="h-3 w-3 inline mr-1" />
                {showVideo ? 'Hide Tutorial' : 'Watch Tutorial'}
              </button>
            </div>

            {showVideo && (
              <div className="rounded-2xl overflow-hidden">
                <ExerciseVideoPlayer exerciseId={currentExercise.exercise_id} />
              </div>
            )}

            {/* Set progress ring */}
            <div className="flex justify-center">
              <ActivityRing progress={setProgress} color="#BF5AF2" size={160} strokeWidth={18}>
                <div className="text-center">
                  <p className="text-3xl font-bold text-white">{setsForCurrent.length}</p>
                  <p className="text-xs" style={{ color: '#8E8E93' }}>/ {currentExercise.sets} sets</p>
                </div>
              </ActivityRing>
            </div>

            {/* Logged sets */}
            {setsForCurrent.length > 0 && (
              <div className="space-y-2">
                {setsForCurrent.map((s, i) => (
                  <div
                    key={i}
                    className="flex justify-between px-4 py-2.5 rounded-2xl text-sm"
                    style={{ background: 'rgba(191,90,242,0.1)' }}
                  >
                    <span style={{ color: '#8E8E93' }}>Set {s.set_number}</span>
                    <span className="font-semibold text-white">
                      {s.weight_kg ?? 'BW'} kg × {s.reps} reps
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Input row */}
            <div
              className="rounded-3xl p-4 space-y-4"
              style={{ background: '#1C1C1E' }}
            >
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="aw-weight" className="text-xs" style={{ color: '#8E8E93' }}>Weight (kg)</Label>
                  <Input
                    id="aw-weight"
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    className="text-white border-0 rounded-xl text-center font-semibold"
                    style={{ background: '#2C2C2E' }}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="aw-reps" className="text-xs" style={{ color: '#8E8E93' }}>Reps</Label>
                  <Input
                    id="aw-reps"
                    type="number"
                    value={reps}
                    onChange={(e) => setReps(e.target.value)}
                    className="text-white border-0 rounded-xl text-center font-semibold"
                    style={{ background: '#2C2C2E' }}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="aw-rpe" className="text-xs" style={{ color: '#8E8E93' }}>RPE (1–10)</Label>
                  <Input
                    id="aw-rpe"
                    type="number"
                    value={rpe}
                    onChange={(e) => setRpe(e.target.value)}
                    className="text-white border-0 rounded-xl text-center font-semibold"
                    style={{ background: '#2C2C2E' }}
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={handleLogSet}
                disabled={!reps || logSet.isPending}
                className="w-full py-3.5 rounded-2xl font-bold text-base transition-all"
                style={
                  reps && !logSet.isPending
                    ? { background: '#ADFF2F', color: '#000', cursor: 'pointer' }
                    : { background: '#2C2C2E', color: '#8E8E93', cursor: 'not-allowed' }
                }
              >
                {logSet.isPending && <Loader2 className="h-4 w-4 animate-spin inline mr-2" />}
                Log Set {setsForCurrent.length + 1}
              </button>
            </div>

            {/* Prev / Next navigation */}
            <div className="flex justify-between">
              <button
                type="button"
                disabled={store.currentExerciseIndex === 0}
                onClick={() => store.setExerciseIndex(store.currentExerciseIndex - 1)}
                className="flex items-center gap-1 px-4 py-2 rounded-full text-sm font-semibold"
                style={{
                  background: '#1C1C1E',
                  color: store.currentExerciseIndex === 0 ? '#8E8E93' : '#fff',
                }}
              >
                <ChevronLeft className="h-4 w-4" /> Prev
              </button>
              {isLastExercise ? (
                <button
                  type="button"
                  onClick={() => setShowEndConfirm(true)}
                  className="flex items-center gap-1 px-4 py-2 rounded-full text-sm font-bold"
                  style={{ background: 'rgba(255,55,95,0.15)', color: '#FF375F' }}
                >
                  <Flag className="h-4 w-4" /> Finish
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    store.setExerciseIndex(store.currentExerciseIndex + 1)
                    setWeight('')
                    setReps('')
                    setRpe('')
                    setShowVideo(false)
                  }}
                  className="flex items-center gap-1 px-4 py-2 rounded-full text-sm font-semibold"
                  style={{ background: '#1C1C1E', color: '#fff' }}
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              )}
            </div>
          </>
        )}
      </div>

      {/* Fixed bottom control bar */}
      <div
        className="fixed bottom-0 left-0 right-0 rounded-t-3xl px-5 pt-4 pb-10"
        style={{ background: '#1C1C1E', boxShadow: '0 -2px 40px rgba(0,0,0,0.8)' }}
      >
        <div className="flex items-center justify-between">
          {/* Workout icon */}
          <div
            className="flex items-center justify-center w-10 h-10 rounded-full"
            style={{ background: 'rgba(173,255,47,0.12)' }}
          >
            <Dumbbell className="h-5 w-5" style={{ color: '#ADFF2F' }} />
          </div>

          {/* Timer */}
          <div className="text-center">
            <p
              className="text-2xl font-mono font-bold"
              style={{ color: '#FFD60A', letterSpacing: '0.05em' }}
            >
              {formatTime(stopwatch.elapsed)}
            </p>
          </div>

          {/* Mini set-progress ring + controls */}
          <div className="flex items-center gap-3">
            <ActivityRing progress={exerciseProgress} color="#FF375F" size={40} strokeWidth={5} />

            <button
              type="button"
              onClick={stopwatch.isRunning ? stopwatch.pause : stopwatch.start}
              className="flex items-center justify-center w-10 h-10 rounded-full"
              style={{ background: '#2C2C2E' }}
            >
              {stopwatch.isRunning
                ? <Pause className="h-4 w-4 text-white" />
                : <Play className="h-4 w-4 text-white" />
              }
            </button>

            <button
              type="button"
              onClick={() => setShowEndConfirm(true)}
              className="flex items-center justify-center w-10 h-10 rounded-full"
              style={{ background: 'rgba(255,55,95,0.15)' }}
            >
              <Flag className="h-4 w-4" style={{ color: '#FF375F' }} />
            </button>
          </div>
        </div>
      </div>

      {/* Rest Timer Dialog */}
      <Dialog open={showRestTimer} onOpenChange={setShowRestTimer}>
        <DialogContent
          className="max-w-sm rounded-3xl border-0 p-8"
          style={{ background: '#1C1C1E' }}
        >
          <DialogHeader>
            <DialogTitle className="text-white text-center">Rest</DialogTitle>
            <DialogDescription className="text-center" style={{ color: '#8E8E93' }}>
              Take a break before your next set
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center gap-6 mt-2">
            <ActivityRing
              progress={restTimer.remaining / restTotal}
              color="#ADFF2F"
              size={200}
              strokeWidth={20}
            >
              <div className="text-center">
                <p className="text-5xl font-mono font-bold text-white">
                  {formatTime(restTimer.remaining)}
                </p>
              </div>
            </ActivityRing>

            <div className="flex gap-2">
              {[30, 60, 90, 120].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => { setRestTotal(s); restTimer.reset(s); restTimer.start() }}
                  className="px-3 py-1.5 rounded-full text-xs font-semibold"
                  style={{ background: '#2C2C2E', color: '#8E8E93' }}
                >
                  {s}s
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={() => setShowRestTimer(false)}
              className="px-8 py-2.5 rounded-full font-semibold text-sm"
              style={{ background: '#ADFF2F', color: '#000' }}
            >
              Skip Rest
            </button>
          </div>
        </DialogContent>
      </Dialog>

      {/* End Confirmation Dialog */}
      <Dialog open={showEndConfirm} onOpenChange={setShowEndConfirm}>
        <DialogContent
          className="max-w-sm rounded-3xl border-0 p-6"
          style={{ background: '#1C1C1E' }}
        >
          <DialogHeader>
            <DialogTitle className="text-white">End Workout?</DialogTitle>
            <DialogDescription style={{ color: '#8E8E93' }}>
              You've logged {store.loggedSets.length} sets. End this workout?
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 justify-end mt-4">
            <button
              type="button"
              onClick={() => setShowEndConfirm(false)}
              className="px-5 py-2.5 rounded-full text-sm font-semibold"
              style={{ background: '#2C2C2E', color: '#fff' }}
            >
              Continue
            </button>
            <button
              type="button"
              onClick={handleEndWorkout}
              disabled={endSession.isPending}
              className="px-5 py-2.5 rounded-full text-sm font-bold"
              style={{ background: '#FF375F', color: '#fff' }}
            >
              {endSession.isPending && <Loader2 className="h-4 w-4 animate-spin inline mr-1" />}
              End Workout
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
