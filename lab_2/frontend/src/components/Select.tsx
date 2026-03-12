import { cn } from "@/lib/utils";
import { SelectHTMLAttributes, forwardRef } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, className, id, ...props }, ref) => (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={id} className="text-xs text-[var(--color-text-muted)] font-medium uppercase tracking-wide">
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={id}
        className={cn(
          "bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md px-3 py-2 text-sm",
          "text-[var(--color-text)] focus:outline-none focus:border-[var(--color-accent)] transition-colors cursor-pointer",
          className,
        )}
        {...props}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  ),
);
Select.displayName = "Select";
