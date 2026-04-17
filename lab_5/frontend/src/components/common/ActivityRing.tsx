import { useEffect, useRef, useState } from 'react'

interface ActivityRingProps {
  progress: number // 0–1
  color: string
  size?: number
  strokeWidth?: number
  children?: React.ReactNode
  className?: string
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
  const targetOffset = circumference * (1 - clampedProgress)

  const [offset, setOffset] = useState(circumference)
  const [animated, setAnimated] = useState(false)
  const mounted = useRef(false)

  useEffect(() => {
    if (mounted.current) return
    mounted.current = true
    const id = requestAnimationFrame(() => {
      setTimeout(() => {
        setOffset(targetOffset)
        setAnimated(true)
      }, 60)
    })
    return () => cancelAnimationFrame(id)
  }, [])

  useEffect(() => {
    if (animated) setOffset(targetOffset)
  }, [targetOffset, animated])

  // tip of the arc position
  const angle = clampedProgress * 2 * Math.PI - Math.PI / 2
  const cx = size / 2 + r * Math.cos(angle)
  const cy = size / 2 + r * Math.sin(angle)
  const showTip = clampedProgress > 0.01

  const gradId = `grad-${color.replace('#', '')}-${size}`
  const filterId = `shadow-${color.replace('#', '')}-${size}`

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
            <stop offset="0%" stopColor={color} stopOpacity="0.6" />
            <stop offset="100%" stopColor={color} stopOpacity="1" />
          </linearGradient>
          <filter id={filterId} x="-50%" y="-50%" width="200%" height="200%">
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

        {/* Progress arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={`url(#${gradId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: animated
              ? 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)'
              : 'none',
          }}
        />

        {/* Drop-shadow tip dot */}
        {showTip && (
          <circle
            cx={cx}
            cy={cy}
            r={strokeWidth / 2}
            fill={color}
            filter={`url(#${filterId})`}
            style={{ transform: 'rotate(0deg)' }}
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
