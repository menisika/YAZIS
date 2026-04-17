import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, MoreVertical, Check, X, Clock, GripVertical } from 'lucide-react'
import {
  DndContext,
  DragEndEvent,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { Card } from '@/components/ui/card'
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
  const config: Record<PlanDayStatus, { label: string; cls: string; Icon: typeof Check | null }> = {
    done: { label: 'Done', cls: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400', Icon: Check },
    skipped: { label: 'Skipped', cls: 'bg-muted-foreground/15 text-muted-foreground', Icon: X },
    today: { label: 'Today', cls: 'bg-primary/15 text-primary', Icon: Clock },
    upcoming: { label: 'Upcoming', cls: 'bg-muted text-muted-foreground', Icon: null },
    rest: { label: 'Rest', cls: 'bg-muted text-muted-foreground', Icon: null },
  }
  const { label, cls, Icon } = config[status]
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${cls}`}>
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

function DayCard({
  dow,
  day,
  isToday,
  isBusy,
  menuOpen,
  onToggleMenu,
  onToggleRest,
  onStart,
}: DayCardProps) {
  const isRest = day?.is_rest ?? true
  const status = day?.status ?? (isRest ? 'rest' : 'upcoming')

  const {
    attributes,
    listeners,
    setNodeRef: setDragRef,
    transform,
    isDragging,
  } = useDraggable({ id: dow })
  const { setNodeRef: setDropRef, isOver } = useDroppable({ id: dow })

  const style: React.CSSProperties = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`, zIndex: 50 }
    : {}

  return (
    <div ref={setDropRef} className={`rounded-2xl ${isOver ? 'ring-2 ring-primary ring-offset-2 ring-offset-background' : ''}`}>
      <div ref={setDragRef} style={style} className={isDragging ? 'opacity-60' : ''}>
        <Card
          className={`p-5 relative transition-shadow ${!isRest ? 'border-l-4 border-l-primary' : 'opacity-80'} ${
            isToday ? 'ring-2 ring-primary ring-offset-2 ring-offset-background' : ''
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 min-w-0">
              <button
                {...attributes}
                {...listeners}
                className="cursor-grab active:cursor-grabbing p-0.5 -ml-1 text-muted-foreground hover:text-foreground touch-none"
                aria-label="Drag to swap day"
                type="button"
              >
                <GripVertical className="h-4 w-4" />
              </button>
              <h3 className="font-semibold">{DAY_NAMES_SHORT[dow]}</h3>
              {isToday && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-primary text-primary-foreground">
                  Today
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <StatusBadge status={status} />
              <div className="relative">
                <button
                  className="p-1 rounded hover:bg-muted transition-colors"
                  onClick={onToggleMenu}
                  disabled={isBusy}
                  type="button"
                >
                  <MoreVertical className="h-4 w-4 text-muted-foreground" />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 top-7 z-20 bg-card border border-border rounded-xl shadow-lg min-w-[160px] py-1">
                    <button
                      className="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors"
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

          {day && !isRest ? (
            <div className="space-y-2">
              <div className="text-xs bg-primary/10 text-primary px-2.5 py-1 rounded-full font-medium inline-block">
                {day.focus}
              </div>
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
                onClick={onStart}
                disabled={!isToday}
                title={isToday ? 'Start today\'s workout' : 'Only today\'s workout can be started'}
              >
                {isToday ? 'Start' : 'Not today'}
              </Button>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">Rest Day</p>
          )}
        </Card>
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

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
  )

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
          <h1 className="text-2xl font-bold tracking-tight">Workout Plan</h1>
          <p className="text-muted-foreground text-sm">
            {activePlan.name}
            <span className="ml-2 text-xs">· Drag a day onto another to swap</span>
          </p>
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

      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
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
