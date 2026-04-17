import { Loader2 } from 'lucide-react'

export default function LoadingSpinner({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#ADFF2F' }} />
      {label && <p className="text-sm" style={{ color: '#8E8E93' }}>{label}</p>}
    </div>
  )
}
