import { useEffect, useRef, useState } from 'react'

interface ActivityRingProps {
  progress: number // 0–1
  color: string
  size?: number
  strokeWidth?: number
  children?: React.ReactNode
  className?: string
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

export default function ActivityRing({
  progress,
  color,
  size = 180,
  strokeWidth = 18,
  children,
  className = '',
}: ActivityRingProps) {
  const clampedProgress = Math.min(1, Math.max(0, progress))
  const r = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * r

  const [animProgress, setAnimProgress] = useState(0)
  const prevProgressRef = useRef(0)
  const animRef = useRef<number | null>(null)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    // Cancel any in-flight animation
    if (animRef.current !== null) {
      cancelAnimationFrame(animRef.current)
      animRef.current = null
    }
    if (timeoutRef.current !== null) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }

    const startValue = prevProgressRef.current
    const targetValue = clampedProgress
    const duration = 1400
    let startTime: number | null = null

    const tick = (now: number) => {
      if (startTime === null) startTime = now
      const elapsed = now - startTime
      const t = Math.min(elapsed / duration, 1)
      const eased = easeOutCubic(t)
      const current = startValue + (targetValue - startValue) * eased

      prevProgressRef.current = current
      setAnimProgress(current)

      if (t < 1) {
        animRef.current = requestAnimationFrame(tick)
      } else {
        animRef.current = null
      }
    }

    timeoutRef.current = setTimeout(() => {
      timeoutRef.current = null
      animRef.current = requestAnimationFrame(tick)
    }, 60)

    return () => {
      if (animRef.current !== null) {
        cancelAnimationFrame(animRef.current)
        animRef.current = null
      }
      if (timeoutRef.current !== null) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
    }
  }, [clampedProgress])

  // Derived geometry from animProgress
  const strokeDashoffset = circumference * (1 - animProgress)
  const angle = animProgress * 2 * Math.PI - Math.PI / 2
  const tipCx = size / 2 + r * Math.cos(angle)
  const tipCy = size / 2 + r * Math.sin(angle)
  const showTip = animProgress > 0.01

  // Dynamic glow on the arc via CSS filter
  const arcGlow =
    animProgress <= 0.01
      ? 'none'
      : `drop-shadow(0 0 ${2 + animProgress * 14}px ${color}) drop-shadow(0 0 ${1 + animProgress * 7}px ${color})`

  // Gradient start-stop opacity scales with animProgress
  const gradStartOpacity = 0.4 + animProgress * 0.5

  const gradId = `grad-${color.replace('#', '')}-${size}`
  const tipFilterId = `shadow-${color.replace('#', '')}-${size}`

  return (
    <div
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        style={{ transform: 'rotate(-90deg)' }}
        overflow="visible"
      >
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity={gradStartOpacity} />
            <stop offset="100%" stopColor={color} stopOpacity="1" />
          </linearGradient>
          <filter id={tipFilterId} x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow
              dx="0"
              dy="0"
              stdDeviation="6"
              floodColor={color}
              floodOpacity="0.95"
            />
          </filter>
        </defs>

        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeOpacity={0.15}
        />

        {/* Progress arc with dynamic CSS glow */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={`url(#${gradId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ filter: arcGlow }}
        />

        {/* Drop-shadow tip dot */}
        {showTip && (
          <circle
            cx={tipCx}
            cy={tipCy}
            r={strokeWidth / 2}
            fill={color}
            filter={`url(#${tipFilterId})`}
          />
        )}
      </svg>

      {children && (
        <div className="absolute inset-0 flex items-center justify-center">
          {children}
        </div>
      )}
    </div>
  )
}
