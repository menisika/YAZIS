import { cn } from "@/lib/utils";
import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, id, ...props }, ref) => (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={id} className="text-xs text-[var(--color-text-muted)] font-medium uppercase tracking-wide">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={id}
        className={cn(
          "bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md px-3 py-2 text-sm",
          "text-[var(--color-text)] placeholder:text-[var(--color-text-muted)]",
          "focus:outline-none focus:border-[var(--color-accent)] transition-colors",
          error && "border-red-500",
          className,
        )}
        {...props}
      />
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  ),
);
Input.displayName = "Input";
