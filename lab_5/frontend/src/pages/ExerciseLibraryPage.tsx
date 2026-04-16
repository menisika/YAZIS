import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Loader2, Search, Dumbbell } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
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
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Exercise Library</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {showAll ? 'All exercises' : 'Exercises in your current plan'}
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search exercises..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={muscleFilter || undefined} onValueChange={(v) => setMuscleFilter(v === 'all' ? '' : v)}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="All muscles" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All muscles</SelectItem>
            {MUSCLE_GROUPS.map((mg) => (
              <SelectItem key={mg} value={mg}>
                {mg.charAt(0).toUpperCase() + mg.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <button
          onClick={() => setShowAll(!showAll)}
          className={`shrink-0 text-xs px-3 py-2 rounded-lg border transition-colors ${
            showAll
              ? 'bg-primary text-primary-foreground border-primary'
              : 'bg-background text-muted-foreground border-border hover:border-primary hover:text-primary'
          }`}
        >
          {showAll ? 'My plan' : 'Show all'}
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {exercises?.map((ex) => (
            <Card
              key={ex.id}
              className="p-5 cursor-pointer hover:shadow-md transition-shadow group"
              onClick={() => setSelectedExercise(ex)}
            >
              <div className="flex items-start gap-3">
                <div className="shrink-0 w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Dumbbell className="h-5 w-5 text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-sm group-hover:text-primary transition-colors">{ex.name}</h3>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{ex.description}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5 mt-3">
                {ex.muscle_groups.map((mg) => (
                  <MuscleGroupBadge key={mg.muscle_group} muscleGroup={mg.muscle_group} isPrimary={mg.is_primary} />
                ))}
              </div>
              <div className="flex gap-2 mt-3">
                <Badge variant="outline" className="text-xs">{ex.equipment}</Badge>
                <Badge variant="outline" className="text-xs">{ex.difficulty}</Badge>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={!!selectedExercise} onOpenChange={(open) => { if (!open) setSelectedExercise(null) }}>
        <DialogContent className="max-w-2xl">
          {selectedExercise && (
            <>
              <DialogHeader>
                <DialogTitle className="text-xl">{selectedExercise.name}</DialogTitle>
                <DialogDescription>{selectedExercise.description}</DialogDescription>
              </DialogHeader>

              <ExerciseVideoPlayer exerciseId={selectedExercise.id} />

              <div className="flex flex-wrap gap-1.5">
                {selectedExercise.muscle_groups.map((mg) => (
                  <MuscleGroupBadge key={mg.muscle_group} muscleGroup={mg.muscle_group} isPrimary={mg.is_primary} />
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-muted rounded-xl">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Equipment</p>
                  <p className="text-sm font-medium mt-1 capitalize">{selectedExercise.equipment}</p>
                </div>
                <div className="p-3 bg-muted rounded-xl">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Difficulty</p>
                  <p className="text-sm font-medium mt-1 capitalize">{selectedExercise.difficulty}</p>
                </div>
                <div className="p-3 bg-muted rounded-xl">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">MET Value</p>
                  <p className="text-sm font-medium mt-1">{selectedExercise.met_value}</p>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="text-sm font-semibold mb-2">Instructions</h4>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{selectedExercise.instructions}</p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
