import { cn } from "@/lib/utils";

type Variant = "default" | "accent" | "success" | "danger" | "muted";

const variants: Record<Variant, string> = {
  default: "bg-[var(--color-surface-raised)] text-[var(--color-text)]",
  accent: "bg-[var(--color-accent-dim)] text-[var(--color-accent)] border border-[var(--color-accent)]",
  success: "bg-green-950 text-green-400 border border-green-800",
  danger: "bg-red-950 text-red-400 border border-red-800",
  muted: "bg-[var(--color-surface)] text-[var(--color-text-muted)]",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
