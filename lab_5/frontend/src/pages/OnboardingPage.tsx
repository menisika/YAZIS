import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useCreateProfile } from '../hooks/useProfile'
import { useAuthStore } from '../stores/authStore'

const WORKOUT_TYPES = [
  'Strength Training', 'Cardio', 'HIIT', 'Yoga', 'Calisthenics',
  'CrossFit', 'Swimming', 'Running', 'Cycling', 'Martial Arts',
]

const INJURY_OPTIONS = [
  'Lower Back', 'Shoulder', 'Knee', 'Wrist', 'Ankle',
  'Neck', 'Hip', 'Elbow', 'None',
]

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
        injuries: form.injuries.filter((i) => i !== 'None'),
      })
      if (user) setUser({ ...user, has_profile: true })
      navigate('/', { replace: true })
    } catch (err) {
      console.error('Profile creation error:', err)
    }
  }

  const steps = [
    <div key="basics" className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
      <div className="space-y-2">
        <Label htmlFor="ob-age">Age</Label>
        <Input id="ob-age" type="number" value={form.age} onChange={(e) => updateField('age', e.target.value)} />
      </div>
      <div className="space-y-2">
        <Label>Gender</Label>
        <Select value={form.gender} onValueChange={(v) => updateField('gender', v)}>
          <SelectTrigger><SelectValue placeholder="Gender" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="male">Male</SelectItem>
            <SelectItem value="female">Female</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="ob-height">Height (cm)</Label>
        <Input id="ob-height" type="number" value={form.height_cm} onChange={(e) => updateField('height_cm', e.target.value)} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="ob-weight">Weight (kg)</Label>
        <Input id="ob-weight" type="number" value={form.weight_kg} onChange={(e) => updateField('weight_kg', e.target.value)} />
      </div>
    </div>,

    <div key="level" className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Fitness Level</h2>
      <div className="space-y-2">
        <Label>Your Fitness Level</Label>
        <Select value={form.fitness_level} onValueChange={(v) => updateField('fitness_level', v)}>
          <SelectTrigger><SelectValue placeholder="Your fitness level" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="beginner">Beginner (0-1 years)</SelectItem>
            <SelectItem value="intermediate">Intermediate (1-3 years)</SelectItem>
            <SelectItem value="advanced">Advanced (3+ years)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor="ob-days">Days per week</Label>
          <Input id="ob-days" type="number" value={form.workout_days_per_week} onChange={(e) => updateField('workout_days_per_week', e.target.value)} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="ob-dur">Session (min)</Label>
          <Input id="ob-dur" type="number" value={form.session_duration_min} onChange={(e) => updateField('session_duration_min', e.target.value)} />
        </div>
      </div>
    </div>,

    <div key="prefs" className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Workout Preferences</h2>
      <p className="text-sm text-muted-foreground mb-3">Select your preferred workout types</p>
      <div className="space-y-3">
        {WORKOUT_TYPES.map((type) => {
          const value = type.toLowerCase().replace(/\s+/g, '_')
          return (
            <div key={type} className="flex items-center space-x-3">
              <Checkbox
                id={`wt-${value}`}
                checked={form.preferred_workout_types.includes(value)}
                onCheckedChange={() => toggleArrayItem('preferred_workout_types', value)}
              />
              <Label htmlFor={`wt-${value}`} className="cursor-pointer">{type}</Label>
            </div>
          )
        })}
      </div>
    </div>,

    <div key="injuries" className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Injuries & Limitations</h2>
      <p className="text-sm text-muted-foreground mb-3">Select any areas of concern so we can adjust your workouts.</p>
      <div className="space-y-3">
        {INJURY_OPTIONS.map((injury) => {
          const value = injury.toLowerCase().replace(/\s+/g, '_')
          return (
            <div key={injury} className="flex items-center space-x-3">
              <Checkbox
                id={`inj-${value}`}
                checked={form.injuries.includes(value)}
                onCheckedChange={() => toggleArrayItem('injuries', value)}
              />
              <Label htmlFor={`inj-${value}`} className="cursor-pointer">{injury}</Label>
            </div>
          )
        })}
      </div>
    </div>,
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 to-accent/5 p-4">
      <Card className="w-full max-w-lg p-8">
        <div className="flex gap-2 mb-8">
          {steps.map((_, i) => (
            <div key={i} className={`h-1 flex-1 rounded-full transition-colors ${i <= step ? 'bg-primary' : 'bg-muted'}`} />
          ))}
        </div>

        {steps[step]}

        <div className="flex justify-between mt-8">
          <Button variant="outline" onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}>
            Back
          </Button>
          {step < steps.length - 1 ? (
            <Button onClick={() => setStep(step + 1)}>
              Next
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={createProfile.isPending}>
              {createProfile.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Complete Setup
            </Button>
          )}
        </div>
      </Card>
    </div>
  )
}
