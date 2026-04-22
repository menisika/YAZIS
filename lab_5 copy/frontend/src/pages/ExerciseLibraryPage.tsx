import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Loader2, Search, Dumbbell, X } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import api from '../config/api'
import MuscleGroupBadge from '../components/common/MuscleGroupBadge'
import ExerciseVideoPlayer from '../components/common/ExerciseVideoPlayer'
import { MUSCLE_GROUPS } from '../lib/muscleGroups'

interface Exercise {
  id: number
  name: string
  description: string
  category: string
  equipment: string
  difficulty: string
  image_url: string | null
  instructions: string
  met_value: number
  muscle_groups: { muscle_group: string; is_primary: boolean }[]
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: '#ADFF2F',
  intermediate: '#FFD60A',
  advanced: '#FF375F',
}

export default function ExerciseLibraryPage() {
  const [search, setSearch] = useState('')
  const [muscleFilter, setMuscleFilter] = useState('')
  const [showAll, setShowAll] = useState(false)
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null)

  const { data: exercises, isLoading } = useQuery<Exercise[]>({
    queryKey: ['exercises', search, muscleFilter, showAll],
    queryFn: async () => {
      const params: Record<string, string> = { limit: '50' }
      if (search) params.search = search
      if (muscleFilter) params.muscle_group = muscleFilter
      if (!showAll) params.scope = 'plan'
      const { data } = await api.get('/exercises', { params })
      return data
    },
  })

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Exercises</h1>
        <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>
          {showAll ? 'All exercises' : 'Exercises in your current plan'}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: '#8E8E93' }} />
          <input
            type="text"
            placeholder="Search exercises…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 rounded-2xl text-sm text-white placeholder-[#8E8E93] outline-none"
            style={{ background: '#1C1C1E', border: '1px solid rgba(255,255,255,0.08)' }}
          />
        </div>
        <Select value={muscleFilter || undefined} onValueChange={(v) => setMuscleFilter(v === 'all' ? '' : v)}>
          <SelectTrigger
            className="w-full sm:w-44 rounded-2xl border-0 text-sm"
            style={{ background: '#1C1C1E', color: muscleFilter ? '#fff' : '#8E8E93' }}
          >
            <SelectValue placeholder="All muscles" />
          </SelectTrigger>
          <SelectContent style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.08)' }}>
            <SelectItem value="all" style={{ color: '#fff' }}>All muscles</SelectItem>
            {MUSCLE_GROUPS.map((mg) => (
              <SelectItem key={mg} value={mg} style={{ color: '#fff' }}>
                {mg.charAt(0).toUpperCase() + mg.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <button
          type="button"
          onClick={() => setShowAll(!showAll)}
          className="shrink-0 text-xs px-4 py-2.5 rounded-2xl font-semibold transition-all"
          style={
            showAll
              ? { background: 'rgba(173,255,47,0.15)', color: '#ADFF2F', border: '1px solid rgba(173,255,47,0.3)' }
              : { background: '#1C1C1E', color: '#8E8E93', border: '1px solid rgba(255,255,255,0.08)' }
          }
        >
          {showAll ? 'My plan' : 'Show all'}
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#ADFF2F' }} />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {exercises?.map((ex) => (
            <button
              key={ex.id}
              type="button"
              onClick={() => setSelectedExercise(ex)}
              className="text-left rounded-3xl p-5 transition-all"
              style={{ background: '#1C1C1E', border: '1px solid rgba(255,255,255,0.05)' }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(173,255,47,0.2)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)')}
            >
              <div className="flex items-start gap-3">
                <div
                  className="shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center"
                  style={{ background: 'rgba(173,255,47,0.1)' }}
                >
                  <Dumbbell className="h-5 w-5" style={{ color: '#ADFF2F' }} />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-sm text-white">{ex.name}</h3>
                  <p className="text-xs mt-1 line-clamp-2" style={{ color: '#8E8E93' }}>{ex.description}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5 mt-3">
                {ex.muscle_groups.map((mg) => (
                  <MuscleGroupBadge key={mg.muscle_group} muscleGroup={mg.muscle_group} isPrimary={mg.is_primary} />
                ))}
              </div>
              <div className="flex gap-2 mt-3">
                <span
                  className="text-[10px] font-semibold px-2.5 py-1 rounded-full"
                  style={{ background: '#2C2C2E', color: '#8E8E93' }}
                >
                  {ex.equipment}
                </span>
                <span
                  className="text-[10px] font-semibold px-2.5 py-1 rounded-full"
                  style={{
                    background: `${DIFFICULTY_COLORS[ex.difficulty] ?? '#8E8E93'}18`,
                    color: DIFFICULTY_COLORS[ex.difficulty] ?? '#8E8E93',
                  }}
                >
                  {ex.difficulty}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Detail Dialog */}
      <Dialog open={!!selectedExercise} onOpenChange={(open) => { if (!open) setSelectedExercise(null) }}>
        <DialogContent
          className="max-w-2xl rounded-3xl border-0 p-6 max-h-[90vh] overflow-y-auto"
          style={{ background: '#1C1C1E' }}
        >
          {selectedExercise && (
            <>
              <DialogHeader>
                <DialogTitle className="text-xl text-white">{selectedExercise.name}</DialogTitle>
                <DialogDescription style={{ color: '#8E8E93' }}>{selectedExercise.description}</DialogDescription>
              </DialogHeader>

              <ExerciseVideoPlayer exerciseId={selectedExercise.id} />

              <div className="flex flex-wrap gap-1.5">
                {selectedExercise.muscle_groups.map((mg) => (
                  <MuscleGroupBadge key={mg.muscle_group} muscleGroup={mg.muscle_group} isPrimary={mg.is_primary} />
                ))}
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                {[
                  { label: 'Equipment', value: selectedExercise.equipment },
                  { label: 'Difficulty', value: selectedExercise.difficulty },
                  { label: 'MET Value', value: selectedExercise.met_value },
                ].map((item) => (
                  <div key={item.label} className="p-3 rounded-2xl" style={{ background: '#2C2C2E' }}>
                    <p className="text-[10px] uppercase font-semibold tracking-wider mb-1" style={{ color: '#8E8E93' }}>
                      {item.label}
                    </p>
                    <p className="text-sm font-semibold text-white capitalize">{item.value}</p>
                  </div>
                ))}
              </div>

              <div style={{ height: 1, background: 'rgba(255,255,255,0.08)' }} />

              <div>
                <h4 className="text-sm font-semibold text-white mb-2">Instructions</h4>
                <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#8E8E93' }}>
                  {selectedExercise.instructions}
                </p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
