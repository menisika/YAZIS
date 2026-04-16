import { Card } from '@/components/ui/card'

interface StatsCardProps {
  label: string
  value: string | number
  icon?: React.ReactNode
  color?: string
}

export default function StatsCard({ label, value, icon }: StatsCardProps) {
  return (
    <Card className="p-5 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3">
        {icon && <div className="text-2xl shrink-0">{icon}</div>}
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground uppercase tracking-wider font-medium">{label}</p>
          <p className="text-2xl font-bold text-foreground mt-0.5 truncate">{value}</p>
        </div>
      </div>
    </Card>
  )
}
