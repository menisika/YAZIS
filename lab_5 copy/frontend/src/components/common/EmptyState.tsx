interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export default function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-5xl mb-4">{icon}</div>}
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="text-sm mt-2 max-w-md" style={{ color: '#8E8E93' }}>{description}</p>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="mt-6 px-6 py-3 rounded-full font-bold text-sm"
          style={{ background: '#ADFF2F', color: '#000' }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  )
}
