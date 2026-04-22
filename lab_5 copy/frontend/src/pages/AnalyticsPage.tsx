import { useState } from 'react'
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
import LoadingSpinner from '../components/common/LoadingSpinner'
import { MUSCLE_GROUP_LABELS } from '../lib/muscleGroups'

const PERIODS = [
  { label: '7d', value: 7 },
  { label: '30d', value: 30 },
  { label: '90d', value: 90 },
]

const TOOLTIP_STYLE = {
  background: '#2C2C2E',
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: 12,
  color: '#fff',
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState(30)

  const { data: summary, isLoading } = useAnalyticsSummary(period)
  const { data: frequency } = useWeeklyFrequency(12)
  const { data: muscles } = useMuscleDistribution(period)
  const { data: calories } = useCalorieHistory(period)

  if (isLoading) return <LoadingSpinner label="Loading analytics…" />

  const muscleData = muscles?.map((m) => ({
    muscle: MUSCLE_GROUP_LABELS[m.muscle_group] || m.muscle_group,
    sets: m.total_sets,
  })) || []

  const stats = [
    { label: 'Sessions', value: summary?.total_sessions ?? 0, color: '#ADFF2F' },
    { label: 'Volume', value: `${Math.round(summary?.total_volume_kg ?? 0)} kg`, color: '#BF5AF2' },
    { label: 'Calories', value: Math.round(summary?.total_calories ?? 0), color: '#FF375F' },
    { label: 'This Week', value: summary?.sessions_this_week ?? 0, color: '#32D2FF' },
  ]

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white tracking-tight">Analytics</h1>
        <div
          className="flex rounded-full p-1 gap-0.5"
          style={{ background: '#1C1C1E' }}
        >
          {PERIODS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setPeriod(p.value)}
              className="px-4 py-1.5 rounded-full text-sm font-semibold transition-all"
              style={
                period === p.value
                  ? { background: '#2C2C2E', color: '#fff' }
                  : { color: '#8E8E93' }
              }
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="rounded-2xl p-4" style={{ background: '#1C1C1E' }}>
            <p className="text-[11px] font-semibold uppercase tracking-wide mb-1" style={{ color: '#8E8E93' }}>
              {s.label}
            </p>
            <p className="text-xl font-bold" style={{ color: s.color }}>
              {s.value}
            </p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Weekly Frequency */}
        <div className="rounded-3xl p-5" style={{ background: '#1C1C1E' }}>
          <h3 className="font-semibold text-white mb-4">Weekly Frequency</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={frequency || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="week" tick={{ fontSize: 9, fill: '#8E8E93' }} axisLine={false} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 9, fill: '#8E8E93' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: 'rgba(173,255,47,0.05)' }} />
              <Bar dataKey="count" fill="#ADFF2F" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Muscle Distribution */}
        <div className="rounded-3xl p-5" style={{ background: '#1C1C1E' }}>
          <h3 className="font-semibold text-white mb-4">Muscle Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={muscleData}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis dataKey="muscle" tick={{ fontSize: 9, fill: '#8E8E93' }} />
              <PolarRadiusAxis tick={{ fontSize: 8, fill: '#8E8E93' }} axisLine={false} />
              <Radar dataKey="sets" stroke="#BF5AF2" fill="#BF5AF2" fillOpacity={0.25} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Calories Over Time */}
        <div className="rounded-3xl p-5 lg:col-span-2" style={{ background: '#1C1C1E' }}>
          <h3 className="font-semibold text-white mb-4">Calories Burned</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={calories || []}>
              <defs>
                <linearGradient id="calGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF375F" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#FF375F" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#8E8E93' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9, fill: '#8E8E93' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Area
                type="monotone"
                dataKey="calories"
                stroke="#FF375F"
                strokeWidth={2}
                fill="url(#calGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
