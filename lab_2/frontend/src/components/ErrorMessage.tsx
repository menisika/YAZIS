import { AlertTriangle } from "lucide-react";

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3 text-red-400 bg-red-950/50 border border-red-900 rounded-lg p-4">
      <AlertTriangle size={18} className="shrink-0" />
      <span className="text-sm">{message}</span>
    </div>
  );
}
