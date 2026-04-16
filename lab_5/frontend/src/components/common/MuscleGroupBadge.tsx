import { Badge } from '@/components/ui/badge'
import { MUSCLE_GROUP_LABELS } from '../../lib/muscleGroups'

export default function MuscleGroupBadge({ muscleGroup, isPrimary = true }: { muscleGroup: string; isPrimary?: boolean }) {
  return (
    <Badge variant={isPrimary ? 'default' : 'secondary'}>
      {MUSCLE_GROUP_LABELS[muscleGroup] || muscleGroup}
    </Badge>
  )
}
