import { useQuery } from '@tanstack/react-query'
import { Skeleton } from '@/components/ui/skeleton'
import api from '../../config/api'

interface ExerciseVideoPlayerProps {
  exerciseId: number
}

export default function ExerciseVideoPlayer({ exerciseId }: ExerciseVideoPlayerProps) {
  const { data, isLoading } = useQuery<{ youtube_video_id: string | null }>({
    queryKey: ['exercise-video', exerciseId],
    queryFn: () => api.get(`/exercises/${exerciseId}/video`).then((r) => r.data),
    staleTime: Infinity,
  })

  if (isLoading) {
    return <Skeleton className="w-full aspect-video rounded-xl" />
  }

  if (!data?.youtube_video_id) {
    return (
      <div className="w-full aspect-video rounded-xl bg-muted flex items-center justify-center">
        <p className="text-sm text-muted-foreground">No tutorial video available</p>
      </div>
    )
  }

  return (
    <iframe
      src={`https://www.youtube.com/embed/${data.youtube_video_id}?rel=0&modestbranding=1`}
      className="w-full aspect-video rounded-xl"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      title="Exercise tutorial"
    />
  )
}
