import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";
import type { Severity } from "@/lib/types";

const severityStyles: Record<Severity, string> = {
  low: "bg-zinc-500/15 text-zinc-300 border-zinc-500/30",
  medium: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  high: "bg-orange-500/15 text-orange-300 border-orange-500/30",
  critical: "bg-red-500/15 text-red-300 border-red-500/30",
};

export function Badge({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <Badge className={severityStyles[severity]}>{severity.toUpperCase()}</Badge>
  );
}
