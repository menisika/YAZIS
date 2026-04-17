import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useCreateProfile } from '../hooks/useProfile'
import { useAuthStore } from '../stores/authStore'
import ActivityRing from '../components/common/ActivityRing'

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
      className="w-full px-4 py-3 rounded-2xl text-sm text-white placeholder-[#636366] outline-none"
      style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.06)' }}
      onFocus={(e) => (e.target.style.borderColor = 'rgba(173,255,47,0.4)')}
      onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.06)')}
    />
  )
}

function DarkLabel({ htmlFor, children }: { htmlFor?: string; children: React.ReactNode }) {
  return (
    <label htmlFor={htmlFor} className="block text-xs font-semibold mb-1.5" style={{ color: '#8E8E93' }}>
      {children}
    </label>
  )
}

function CheckPill({ label, checked, onToggle }: { label: string; checked: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="text-sm font-medium px-4 py-2 rounded-full transition-all"
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

export default function OnboardingPage() {
  const navigate = useNavigate()
  const createProfile = useCreateProfile()
  const { setUser, user } = useAuthStore()
  const [step, setStep] = useState(0)

  const [form, setForm] = useState({
    age: '',
    gender: 'male',
    height_cm: '',
    weight_kg: '',
    fitness_level: 'beginner',
    preferred_workout_types: [] as string[],
    workout_days_per_week: '4',
    session_duration_min: '60',
    calorie_goal: '500',
    injuries: [] as string[],
  })

  const updateField = (field: string, value: string | string[]) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const toggleArrayItem = (field: 'preferred_workout_types' | 'injuries', value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value],
    }))
  }

  const handleSubmit = async () => {
    try {
      await createProfile.mutateAsync({
        age: Number(form.age),
        gender: form.gender,
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        fitness_level: form.fitness_level,
        preferred_workout_types: form.preferred_workout_types,
        workout_days_per_week: Number(form.workout_days_per_week),
        session_duration_min: Number(form.session_duration_min),
        calorie_goal: Number(form.calorie_goal),
        injuries: form.injuries.filter((i) => i !== 'None'),
      })
      if (user) setUser({ ...user, has_profile: true })
      navigate('/', { replace: true })
    } catch (err) {
      console.error('Profile creation error:', err)
    }
  }

  const STEP_TITLES = ['Body Info', 'Fitness Level', 'Preferences', 'Limitations']

  const steps = [
    <div key="basics" className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white">Basic Information</h2>
        <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>Tell us about yourself</p>
      </div>
      <div>
        <DarkLabel htmlFor="ob-age">Age</DarkLabel>
        <DarkInput id="ob-age" type="number" value={form.age} onChange={(v) => updateField('age', v)} placeholder="e.g. 25" />
      </div>
      <div>
        <DarkLabel>Gender</DarkLabel>
        <Select value={form.gender} onValueChange={(v) => updateField('gender', v)}>
          <SelectTrigger className="w-full rounded-2xl border-0 text-white" style={{ background: '#2C2C2E' }}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.08)' }}>
            <SelectItem value="male" style={{ color: '#fff' }}>Male</SelectItem>
            <SelectItem value="female" style={{ color: '#fff' }}>Female</SelectItem>
            <SelectItem value="other" style={{ color: '#fff' }}>Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <DarkLabel htmlFor="ob-height">Height (cm)</DarkLabel>
          <DarkInput id="ob-height" type="number" value={form.height_cm} onChange={(v) => updateField('height_cm', v)} placeholder="175" />
        </div>
        <div>
          <DarkLabel htmlFor="ob-weight">Weight (kg)</DarkLabel>
          <DarkInput id="ob-weight" type="number" value={form.weight_kg} onChange={(v) => updateField('weight_kg', v)} placeholder="70" />
        </div>
      </div>
    </div>,

    <div key="level" className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white">Fitness Level</h2>
        <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>How experienced are you?</p>
      </div>
      <div>
        <DarkLabel>Your Fitness Level</DarkLabel>
        <Select value={form.fitness_level} onValueChange={(v) => updateField('fitness_level', v)}>
          <SelectTrigger className="w-full rounded-2xl border-0 text-white" style={{ background: '#2C2C2E' }}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent style={{ background: '#2C2C2E', border: '1px solid rgba(255,255,255,0.08)' }}>
            <SelectItem value="beginner" style={{ color: '#fff' }}>Beginner (0–1 years)</SelectItem>
            <SelectItem value="intermediate" style={{ color: '#fff' }}>Intermediate (1–3 years)</SelectItem>
            <SelectItem value="advanced" style={{ color: '#fff' }}>Advanced (3+ years)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <DarkLabel htmlFor="ob-days">Days / week</DarkLabel>
          <DarkInput id="ob-days" type="number" value={form.workout_days_per_week} onChange={(v) => updateField('workout_days_per_week', v)} />
        </div>
        <div>
          <DarkLabel htmlFor="ob-dur">Session (min)</DarkLabel>
          <DarkInput id="ob-dur" type="number" value={form.session_duration_min} onChange={(v) => updateField('session_duration_min', v)} />
        </div>
      </div>
      <div>
        <DarkLabel htmlFor="ob-calories">Weekly Calorie Burn Goal (kcal)</DarkLabel>
        <DarkInput id="ob-calories" type="number" value={form.calorie_goal} onChange={(v) => updateField('calorie_goal', v)} placeholder="500" />
      </div>
    </div>,

    <div key="prefs" className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white">Workout Preferences</h2>
        <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>Select all that apply</p>
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
    </div>,

    <div key="injuries" className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white">Injuries & Limitations</h2>
        <p className="text-sm mt-0.5" style={{ color: '#8E8E93' }}>Select any areas of concern</p>
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
    </div>,
  ]

  const progress = (step + 1) / steps.length

  return (
    <div className="min-h-screen flex items-center justify-center bg-black p-4">
      <div className="w-full max-w-md">
        {/* Progress ring header */}
        <div className="flex items-center gap-5 mb-8">
          <ActivityRing progress={progress} color="#ADFF2F" size={64} strokeWidth={8}>
            <span className="text-[10px] font-bold text-white">{step + 1}/{steps.length}</span>
          </ActivityRing>
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#8E8E93' }}>
              Step {step + 1} of {steps.length}
            </p>
            <p className="font-bold text-white">{STEP_TITLES[step]}</p>
          </div>
        </div>

        {/* Step dots */}
        <div className="flex gap-2 mb-8">
          {steps.map((_, i) => (
            <div
              key={i}
              className="h-1 flex-1 rounded-full transition-all"
              style={{ background: i <= step ? '#ADFF2F' : '#2C2C2E' }}
            />
          ))}
        </div>

        {/* Form card */}
        <div className="rounded-3xl p-6 space-y-6" style={{ background: '#1C1C1E' }}>
          {steps[step]}

          <div className="flex justify-between pt-2">
            <button
              type="button"
              onClick={() => setStep(Math.max(0, step - 1))}
              disabled={step === 0}
              className="px-5 py-2.5 rounded-full text-sm font-semibold transition-all"
              style={step === 0
                ? { background: '#2C2C2E', color: '#636366', cursor: 'not-allowed' }
                : { background: '#2C2C2E', color: '#fff', cursor: 'pointer' }
              }
            >
              Back
            </button>
            {step < steps.length - 1 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="px-6 py-2.5 rounded-full text-sm font-bold"
                style={{ background: '#ADFF2F', color: '#000' }}
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={createProfile.isPending}
                className="flex items-center gap-2 px-6 py-2.5 rounded-full text-sm font-bold"
                style={{ background: '#ADFF2F', color: '#000', cursor: createProfile.isPending ? 'not-allowed' : 'pointer' }}
              >
                {createProfile.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Complete Setup
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
