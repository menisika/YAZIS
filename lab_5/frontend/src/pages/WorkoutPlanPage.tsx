import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, MoreVertical, Check, X, Clock, GripVertical, Play } from 'lucide-react'
import type { DragEndEvent } from '@dnd-kit/core'
import {
  DndContext,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { Button } from '@/components/ui/button'
import EmptyState from '../components/common/EmptyState'
import {
  useWorkoutPlans,
  useGenerateWorkout,
  useSwapDays,
  useToggleRest,
  type PlanDay,
  type PlanDayStatus,
} from '../hooks/useWorkout'
import { DAY_NAMES_SHORT } from '../lib/formatters'

const TODAY_IDX = (new Date().getDay() + 6) % 7

function StatusBadge({ status }: { status: PlanDayStatus }) {
  const cfg: Record<PlanDayStatus, { label: string; bg: string; color: string; Icon: typeof Check | null }> = {
    done: { label: 'Done', bg: 'rgba(173,255,47,0.15)', color: '#ADFF2F', Icon: Check },
    skipped: { label: 'Skipped', bg: 'rgba(142,142,147,0.15)', color: '#8E8E93', Icon: X },
    today: { label: 'Today', bg: 'rgba(173,255,47,0.2)', color: '#ADFF2F', Icon: Clock },
    upcoming: { label: 'Upcoming', bg: 'rgba(142,142,147,0.1)', color: '#8E8E93', Icon: null },
    rest: { label: 'Rest', bg: 'rgba(142,142,147,0.1)', color: '#8E8E93', Icon: null },
  }
  const { label, bg, color, Icon } = cfg[status]
  return (
    <span
      className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full"
      style={{ background: bg, color }}
    >
      {Icon && <Icon className="h-3 w-3" />}
      {label}
    </span>
  )
}

interface DayCardProps {
  dow: number
  day: PlanDay | undefined
  isToday: boolean
  isBusy: boolean
  menuOpen: boolean
  onToggleMenu: () => void
  onToggleRest: () => void
  onStart: () => void
}

function DayCard({ dow, day, isToday, isBusy, menuOpen, onToggleMenu, onToggleRest, onStart }: DayCardProps) {
  const isRest = day?.is_rest ?? true
  const status = day?.status ?? (isRest ? 'rest' : 'upcoming')
  const [showExercises, setShowExercises] = useState(false)

  const { attributes, listeners, setNodeRef: setDragRef, transform, isDragging } = useDraggable({ id: dow })
  const { setNodeRef: setDropRef, isOver } = useDroppable({ id: dow })

  const style: React.CSSProperties = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`, zIndex: 50 }
    : {}

  const cardBg = isRest ? '#1C1C1E' : '#132208'
  const cardBorder = isToday ? '#ADFF2F' : isRest ? 'rgba(255,255,255,0.06)' : 'rgba(173,255,47,0.18)'

  return (
    <div ref={setDropRef} className={`rounded-3xl ${isOver ? 'ring-2 ring-[#ADFF2F] ring-offset-2 ring-offset-black' : ''}`}>
      <div ref={setDragRef} style={style} className={isDragging ? 'opacity-50' : ''}>
        <div
          className="p-4 rounded-3xl transition-all"
          style={{
            background: cardBg,
            border: `1.5px solid ${cardBorder}`,
            boxShadow: isToday ? '0 0 20px rgba(173,255,47,0.08)' : undefined,
          }}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 min-w-0">
              <button
                {...attributes}
                {...listeners}
                className="cursor-grab active:cursor-grabbing p-0.5 -ml-1 touch-none"
                style={{ color: '#8E8E93' }}
                aria-label="Drag to swap day"
                type="button"
              >
                <GripVertical className="h-4 w-4" />
              </button>
              <h3 className="font-bold text-white">{DAY_NAMES_SHORT[dow]}</h3>
            </div>
            <div className="flex items-center gap-1.5">
              <StatusBadge status={status} />
              <div className="relative">
                <button
                  className="p-1 rounded-lg hover:bg-white/5 transition-colors"
                  onClick={onToggleMenu}
                  disabled={isBusy}
                  type="button"
                >
                  <MoreVertical className="h-4 w-4" style={{ color: '#8E8E93' }} />
                </button>
                {menuOpen && (
                  <div
                    className="absolute right-0 top-7 z-20 rounded-2xl shadow-2xl min-w-[160px] py-1"
                    style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.08)' }}
                  >
                    <button
                      className="w-full text-left px-4 py-2.5 text-sm text-white hover:bg-white/5 transition-colors"
                      onClick={onToggleRest}
                      type="button"
                    >
                      {isRest ? 'Make workout day' : 'Make rest day'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Content */}
          {day && !isRest ? (
            <div className="space-y-2">
              <div
                className="text-[11px] font-bold px-2.5 py-1 rounded-full inline-block"
                style={{ background: 'rgba(173,255,47,0.15)', color: '#ADFF2F' }}
              >
                {day.focus}
              </div>
              <div className={showExercises ? '' : 'hidden sm:block'}>
                {day.exercises.slice(0, 4).map((ex) => (
                  <div key={ex.id} className="flex justify-between text-xs" style={{ color: '#8E8E93' }}>
                    <span className="truncate mr-2 text-white/80">{ex.exercise_name}</span>
                    <span className="whitespace-nowrap font-semibold">
                      {ex.sets}×{ex.reps_min}–{ex.reps_max}
                    </span>
                  </div>
                ))}
                {day.exercises.length > 4 && (
                  <p className="text-[10px]" style={{ color: '#8E8E93' }}>+{day.exercises.length - 4} more</p>
                )}
              </div>
              <button
                type="button"
                className="sm:hidden w-full text-xs font-semibold py-1.5 rounded-xl transition-colors"
                style={{ color: '#8E8E93', background: 'rgba(255,255,255,0.04)' }}
                onClick={() => setShowExercises((v) => !v)}
              >
                {showExercises ? 'Hide exercises' : `${day.exercises.length} exercises ▾`}
              </button>
              <button
                type="button"
                onClick={isToday ? onStart : undefined}
                disabled={!isToday}
                className="w-full mt-3 flex items-center justify-center gap-2 py-2.5 rounded-2xl font-bold text-sm transition-all"
                style={
                  isToday
                    ? { background: '#ADFF2F', color: '#000', cursor: 'pointer' }
                    : { background: 'rgba(173,255,47,0.08)', color: '#8E8E93', cursor: 'not-allowed' }
                }
              >
                <Play className="h-4 w-4 fill-current" />
                {isToday ? 'Start' : 'Not today'}
              </button>
            </div>
          ) : (
            <p className="text-sm" style={{ color: '#8E8E93' }}>Rest Day</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function WorkoutPlanPage() {
  const navigate = useNavigate()
  const { data: plans, isLoading } = useWorkoutPlans()
  const generateWorkout = useGenerateWorkout()
  const swapDays = useSwapDays()
  const toggleRest = useToggleRest()

  const [openMenu, setOpenMenu] = useState<number | null>(null)

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }))
  const activePlan = plans?.[0]

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#ADFF2F' }} />
      </div>
    )
  }

  if (!activePlan) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">Workout</h1>
        <EmptyState
          icon="📋"
          title="No workout plan yet"
          description="Let AI create a personalized weekly plan based on your profile and goals."
          actionLabel={generateWorkout.isPending ? 'Generating…' : 'Generate My Plan'}
          onAction={() => generateWorkout.mutateAsync({})}
        />
      </div>
    )
  }

  const handleToggleRest = async (dow: number) => {
    setOpenMenu(null)
    await toggleRest.mutateAsync(dow)
  }

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || over.id === active.id) return
    await swapDays.mutateAsync({ day_a: Number(active.id), day_b: Number(over.id) })
  }

  const isBusy = swapDays.isPending || toggleRest.isPending

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Workout</h1>
          <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>
            {activePlan.name} · drag to swap days
          </p>
        </div>
        <button
          type="button"
          disabled={generateWorkout.isPending}
          onClick={() => generateWorkout.mutateAsync({})}
          className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold transition-all"
          style={{ background: '#1C1C1E', color: '#ADFF2F', border: '1px solid rgba(173,255,47,0.3)' }}
        >
          {generateWorkout.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
          Regenerate
        </button>
      </div>

      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {Array.from({ length: 7 }, (_, i) => {
            const day = activePlan.days.find((d) => d.day_of_week === i)
            return (
              <DayCard
                key={i}
                dow={i}
                day={day}
                isToday={i === TODAY_IDX}
                isBusy={isBusy}
                menuOpen={openMenu === i}
                onToggleMenu={() => setOpenMenu(openMenu === i ? null : i)}
                onToggleRest={() => handleToggleRest(i)}
                onStart={() => navigate(`/workout/${activePlan.id}/${i}`)}
              />
            )
          })}
        </div>
      </DndContext>

      {openMenu !== null && (
        <div className="fixed inset-0 z-10" onClick={() => setOpenMenu(null)} />
      )}
    </div>
  )
}
