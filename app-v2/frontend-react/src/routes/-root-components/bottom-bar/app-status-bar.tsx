import { Badge } from "#/components/ui/badge";
import { CONSTANTS } from "@/constants";
import { useFirstRender } from "#/utils/hooks/use-first-render";

export function AppStatusBar() {
  const isFirstRender = useFirstRender();

  if (isFirstRender) {
    return null;
  }

  return (
    <div
      data-comp="AppStatusBar"
      role="region"
      aria-label="App Status Bar"
      className="flex flex-row gap-2 items-center text-xs text-muted-foreground"
    >
      <span
        aria-label="App Name"
      >
        SpotiDisk
      </span>
      <span
        aria-label="App Version"
      >
        v{CONSTANTS.APP_VERSION}
      </span>
      {CONSTANTS.FRONTEND_APP_MODE === 'DEV' && (
        <Badge
          aria-label="App Mode"
          variant="outline"
        >
          DEV
        </Badge>
      )}
    </div>
  );
}