import { useGlobalDebugVisibility } from "#/state/global.debug-visibility";
import { InfoIcon } from "lucide-react";
import { TooltipEasy } from "./tooltip-easy";
import { cn } from "#/lib/utils";

/** React Component - Render children if debug mode is enabled */
export function DebugOnly({ children }: { children: React.ReactNode; }) {
  const debugApi = useGlobalDebugVisibility();
  if (!debugApi.isVisible) {
    return null;
  }
  return <>{children}</>;
}


export function DebugOnlyTooltipData({
  data,
  className,
}: {
  data: unknown;
  className?: React.ComponentProps<"div">["className"];
}) {
  return (
    <DebugOnly>
      <TooltipEasy
        classNameContent="w-180 max-w-[90dvw] bg-muted-foreground"
        tooltipText={(
          <pre className="w-180 max-h-[90dvh] overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      >
        <InfoIcon className={cn("size-[1em] text-muted-foreground", className)} />
      </TooltipEasy>
    </DebugOnly>
  );
}