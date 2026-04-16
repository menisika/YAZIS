import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area,
} from 'recharts'
import {
  useWeeklyFrequency,
  useMuscleDistribution,
  useCalorieHistory,
  useAnalyticsSummary,
} from '../hooks/useAnalytics'
import StatsCard from '../components/common/StatsCard'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { MUSCLE_GROUP_LABELS } from '../lib/muscleGroups'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState(30)

  const { data: summary, isLoading } = useAnalyticsSummary(period)
  const { data: frequency } = useWeeklyFrequency(12)
  const { data: muscles } = useMuscleDistribution(period)
  const { data: calories } = useCalorieHistory(period)

  if (isLoading) return <LoadingSpinner label="Loading analytics..." />

  const muscleData = muscles?.map((m) => ({
    muscle: MUSCLE_GROUP_LABELS[m.muscle_group] || m.muscle_group,
    sets: m.total_sets,
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <Tabs value={String(period)} onValueChange={(v) => setPeriod(Number(v))}>
          <TabsList>
            <TabsTrigger value="7">7d</TabsTrigger>
            <TabsTrigger value="30">30d</TabsTrigger>
            <TabsTrigger value="90">90d</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard label="Sessions" value={summary?.total_sessions ?? 0} icon="🏋️" />
        <StatsCard label="Volume" value={`${Math.round(summary?.total_volume_kg ?? 0)}kg`} icon="📊" />
        <StatsCard label="Calories" value={Math.round(summary?.total_calories ?? 0)} icon="🔥" />
        <StatsCard label="This Week" value={summary?.sessions_this_week ?? 0} icon="📅" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-5">
          <h3 className="font-semibold mb-4">Weekly Frequency</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={frequency || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="week" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis allowDecimals={false} stroke="hsl(var(--muted-foreground))" />
              <Tooltip contentStyle={{ borderRadius: '0.75rem', border: '1px solid hsl(var(--border))' }} />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-5">
          <h3 className="font-semibold mb-4">Muscle Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <RadarChart data={muscleData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis dataKey="muscle" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
              <PolarRadiusAxis stroke="hsl(var(--muted-foreground))" />
              <Radar dataKey="sets" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-5 lg:col-span-2">
          <h3 className="font-semibold mb-4">Calories Burned Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={calories || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip contentStyle={{ borderRadius: '0.75rem', border: '1px solid hsl(var(--border))' }} />
              <Area type="monotone" dataKey="calories" stroke="hsl(var(--chart-4))" fill="hsl(var(--chart-4))" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}
