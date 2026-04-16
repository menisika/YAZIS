import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2 } from 'lucide-react'
import { useProfile, useUpdateProfile } from '../hooks/useProfile'
import { useAuthStore } from '../stores/authStore'
import LoadingSpinner from '../components/common/LoadingSpinner'

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
      })
    }
  }, [profile])

  const handleSave = async () => {
    await updateProfile.mutateAsync({
      age: Number(form.age),
      gender: form.gender,
      height_cm: Number(form.height_cm),
      weight_kg: Number(form.weight_kg),
      fitness_level: form.fitness_level,
      workout_days_per_week: Number(form.workout_days_per_week),
      session_duration_min: Number(form.session_duration_min),
    })
  }

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Profile</h1>

      <Card className="p-6">
        <div className="mb-6">
          <p className="text-lg font-semibold">{user?.display_name || 'User'}</p>
          <p className="text-sm text-muted-foreground">{user?.email}</p>
        </div>

        {profile && (
          <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-muted rounded-xl">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">BMR</p>
              <p className="text-lg font-bold mt-0.5">{Math.round(profile.bmr)} cal</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">TDEE</p>
              <p className="text-lg font-bold mt-0.5">{Math.round(profile.tdee)} cal</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="age">Age</Label>
            <Input id="age" type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>Gender</Label>
            <Select value={form.gender} onValueChange={(v) => setForm({ ...form, gender: v })}>
              <SelectTrigger><SelectValue placeholder="Gender" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="height">Height (cm)</Label>
            <Input id="height" type="number" value={form.height_cm} onChange={(e) => setForm({ ...form, height_cm: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="weight">Weight (kg)</Label>
            <Input id="weight" type="number" value={form.weight_kg} onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>Fitness Level</Label>
            <Select value={form.fitness_level} onValueChange={(v) => setForm({ ...form, fitness_level: v })}>
              <SelectTrigger><SelectValue placeholder="Fitness Level" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="days">Days/Week</Label>
            <Input id="days" type="number" value={form.workout_days_per_week} onChange={(e) => setForm({ ...form, workout_days_per_week: e.target.value })} />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button onClick={handleSave} disabled={updateProfile.isPending}>
            {updateProfile.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
            Save Changes
          </Button>
          <Button variant="destructive" onClick={() => signOut()}>
            Sign Out
          </Button>
        </div>
      </Card>
    </div>
  )
}
