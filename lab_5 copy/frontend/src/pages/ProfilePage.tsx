import { useState, useEffect } from 'react'
import { Loader2, LogOut } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useProfile, useUpdateProfile } from '../hooks/useProfile'
import { useAuthStore } from '../stores/authStore'
import LoadingSpinner from '../components/common/LoadingSpinner'

const WORKOUT_TYPES = [
  'Strength Training', 'Cardio', 'HIIT', 'Yoga', 'Calisthenics',
  'CrossFit', 'Swimming', 'Running', 'Cycling', 'Martial Arts',
]

const INJURY_OPTIONS = [
  'Lower Back', 'Shoulder', 'Knee', 'Wrist', 'Ankle',
  'Neck', 'Hip', 'Elbow', 'None',
]

function DarkInput({
  id, type = 'text', value, onChange, placeholder,
}: {
  id?: string
  type?: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full px-4 py-2.5 rounded-2xl text-sm text-white placeholder-[#636366] outline-none"
      style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.06)' }}
      onFocus={(e) => (e.target.style.borderColor = 'rgba(173,255,47,0.4)')}
      onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.06)')}
    />
  )
}

function DarkLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-semibold mb-1.5" style={{ color: '#8E8E93' }}>
      {children}
    </p>
  )
}

function CheckPill({
  label, checked, onToggle,
}: {
  label: string
  checked: boolean
  onToggle: () => void
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="text-xs font-semibold px-3 py-1.5 rounded-full transition-all text-left"
      style={
        checked
          ? { background: 'rgba(173,255,47,0.15)', color: '#ADFF2F', border: '1px solid rgba(173,255,47,0.35)' }
          : { background: '#2C2C2E', color: '#8E8E93', border: '1px solid rgba(255,255,255,0.06)' }
      }
    >
      {checked ? '✓ ' : ''}{label}
    </button>
  )
}

export default function ProfilePage() {
  const { data: profile, isLoading } = useProfile()
  const updateProfile = useUpdateProfile()
  const { user, signOut } = useAuthStore()

  const [form, setForm] = useState({
    age: '',
    gender: '',
    height_cm: '',
    weight_kg: '',
    fitness_level: '',
    workout_days_per_week: '',
    session_duration_min: '',
    calorie_goal: '500',
    preferred_workout_types: [] as string[],
    injuries: [] as string[],
  })

  useEffect(() => {
    if (profile) {
      setForm({
        age: String(profile.age),
        gender: profile.gender,
        height_cm: String(profile.height_cm),
        weight_kg: String(profile.weight_kg),
        fitness_level: profile.fitness_level,
        workout_days_per_week: String(profile.workout_days_per_week),
        session_duration_min: String(profile.session_duration_min),
        calorie_goal: String(profile.calorie_goal ?? 500),
        preferred_workout_types: profile.preferred_workout_types,
        injuries: profile.injuries,
      })
    }
  }, [profile])

  const toggleArrayItem = (field: 'preferred_workout_types' | 'injuries', value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value],
    }))
  }

  const handleSave = async () => {
    await updateProfile.mutateAsync({
      age: Number(form.age),
      gender: form.gender,
      height_cm: Number(form.height_cm),
      weight_kg: Number(form.weight_kg),
      fitness_level: form.fitness_level,
      workout_days_per_week: Number(form.workout_days_per_week),
      session_duration_min: Number(form.session_duration_min),
      calorie_goal: Number(form.calorie_goal),
      preferred_workout_types: form.preferred_workout_types,
      injuries: form.injuries.filter((i) => i !== 'none'),
    })
  }

  if (isLoading) return <LoadingSpinner />

  const bmr = profile ? Math.round(profile.bmr) : null
  const tdee = profile ? Math.round(profile.tdee) : null

  return (
    <div className="space-y-5 max-w-2xl">
      <h1 className="text-2xl font-bold text-white tracking-tight">Profile</h1>

      {/* User card */}
      <div className="rounded-3xl p-5" style={{ background: '#1C1C1E' }}>
        <p className="text-lg font-bold text-white">{user?.display_name || 'User'}</p>
        <p className="text-sm" style={{ color: '#8E8E93' }}>{user?.email}</p>

        {profile && (
          <div className="flex gap-3 mt-5">
            <div className="rounded-xl p-3 flex-1" style={{ background: '#2C2C2E' }}>
              <p className="text-[10px] uppercase font-semibold" style={{ color: '#8E8E93' }}>BMR</p>
              <p className="text-base font-bold" style={{ color: '#BF5AF2' }}>{bmr} cal</p>
            </div>
            <div className="rounded-xl p-3 flex-1" style={{ background: '#2C2C2E' }}>
              <p className="text-[10px] uppercase font-semibold" style={{ color: '#8E8E93' }}>TDEE</p>
              <p className="text-base font-bold" style={{ color: '#FF375F' }}>{tdee} cal</p>
            </div>
          </div>
        )}
      </div>

      {/* Basic info */}
      <div className="rounded-3xl p-5 space-y-4" style={{ background: '#1C1C1E' }}>
        <h2 className="font-bold text-white">Body & Fitness</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <DarkLabel>Age</DarkLabel>
            <DarkInput id="age" type="number" value={form.age} onChange={(v) => setForm({ ...form, age: v })} />
          </div>
          <div>
            <DarkLabel>Gender</DarkLabel>
            <Select value={form.gender} onValueChange={(v) => setForm({ ...form, gender: v })}>
              <SelectTrigger
                className="w-full rounded-2xl border-0 text-sm text-white"
                style={{ background: '#2C2C2E' }}
              >
                <SelectValue placeholder="Gender" />
              </SelectTrigger>
              <SelectContent style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.08)' }}>
                <SelectItem value="male" style={{ color: '#fff' }}>Male</SelectItem>
                <SelectItem value="female" style={{ color: '#fff' }}>Female</SelectItem>
                <SelectItem value="other" style={{ color: '#fff' }}>Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <DarkLabel>Height (cm)</DarkLabel>
            <DarkInput id="height" type="number" value={form.height_cm} onChange={(v) => setForm({ ...form, height_cm: v })} />
          </div>
          <div>
            <DarkLabel>Weight (kg)</DarkLabel>
            <DarkInput id="weight" type="number" value={form.weight_kg} onChange={(v) => setForm({ ...form, weight_kg: v })} />
          </div>
          <div>
            <DarkLabel>Fitness Level</DarkLabel>
            <Select value={form.fitness_level} onValueChange={(v) => setForm({ ...form, fitness_level: v })}>
              <SelectTrigger
                className="w-full rounded-2xl border-0 text-sm text-white"
                style={{ background: '#2C2C2E' }}
              >
                <SelectValue placeholder="Fitness Level" />
              </SelectTrigger>
              <SelectContent style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.08)' }}>
                <SelectItem value="beginner" style={{ color: '#fff' }}>Beginner</SelectItem>
                <SelectItem value="intermediate" style={{ color: '#fff' }}>Intermediate</SelectItem>
                <SelectItem value="advanced" style={{ color: '#fff' }}>Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <DarkLabel>Days / Week</DarkLabel>
            <DarkInput type="number" value={form.workout_days_per_week} onChange={(v) => setForm({ ...form, workout_days_per_week: v })} />
          </div>
        </div>
      </div>

      {/* Goals */}
      <div className="rounded-3xl p-5 space-y-4" style={{ background: '#1C1C1E' }}>
        <h2 className="font-bold text-white">Goals</h2>
        <div>
          <DarkLabel>Weekly Calorie Burn Goal (kcal)</DarkLabel>
          <DarkInput
            type="number"
            value={form.calorie_goal}
            onChange={(v) => setForm({ ...form, calorie_goal: v })}
            placeholder="500"
          />
        </div>
      </div>

      {/* Workout preferences */}
      <div className="rounded-3xl p-5 space-y-3" style={{ background: '#1C1C1E' }}>
        <div>
          <h2 className="font-bold text-white">Workout Preferences</h2>
          <p className="text-xs mt-0.5" style={{ color: '#8E8E93' }}>Select your preferred workout types</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {WORKOUT_TYPES.map((type) => {
            const value = type.toLowerCase().replace(/\s+/g, '_')
            return (
              <CheckPill
                key={type}
                label={type}
                checked={form.preferred_workout_types.includes(value)}
                onToggle={() => toggleArrayItem('preferred_workout_types', value)}
              />
            )
          })}
        </div>
      </div>

      {/* Injuries */}
      <div className="rounded-3xl p-5 space-y-3" style={{ background: '#1C1C1E' }}>
        <div>
          <h2 className="font-bold text-white">Injuries & Limitations</h2>
          <p className="text-xs mt-0.5" style={{ color: '#8E8E93' }}>Select any areas of concern</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {INJURY_OPTIONS.map((injury) => {
            const value = injury.toLowerCase().replace(/\s+/g, '_')
            return (
              <CheckPill
                key={injury}
                label={injury}
                checked={form.injuries.includes(value)}
                onToggle={() => toggleArrayItem('injuries', value)}
              />
            )
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={updateProfile.isPending}
          className="flex items-center gap-2 px-6 py-3 rounded-full font-bold text-sm transition-all"
          style={{ background: '#ADFF2F', color: '#000', cursor: updateProfile.isPending ? 'not-allowed' : 'pointer' }}
        >
          {updateProfile.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          Save Changes
        </button>
        <button
          type="button"
          onClick={() => signOut()}
          className="flex items-center gap-2 px-6 py-3 rounded-full font-bold text-sm transition-all"
          style={{ background: 'rgba(255,55,95,0.12)', color: '#FF375F', border: '1px solid rgba(255,55,95,0.2)' }}
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </div>
  )
}
