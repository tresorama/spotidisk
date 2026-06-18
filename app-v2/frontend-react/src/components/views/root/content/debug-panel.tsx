
import { useGlobalDebugVisibility } from "#/state/global.debug-visibility";
import { EventsLogs } from "#/components/views/root/content/events-logs";
import { Button } from "@/components/ui/button";

export function DebugPanelToggler() {
  const debugVisibility = useGlobalDebugVisibility();

  return (
    <Button
      onClick={debugVisibility.toggleIsVisible}
      variant="secondary"
    >
      Debug
    </Button>
  );
}

export function DebugPanel() {
  const debugVisibility = useGlobalDebugVisibility();

  if (!debugVisibility.isVisible) {
    return null;
  }

  return (
    <UIDebugPanelWrapper>
      <EventsLogs />
    </UIDebugPanelWrapper>
  );
}



// ui

function UIDebugPanelWrapper({ children }: { children: React.ReactNode; }) {
  return (
    <div className="min-h-0 min-w-0 h-70 w-full max-w-full overflow-hidden flex flex-col border-t bg-muted/20">
      <p className="px-4 py-3 text-xs/none text-muted-foreground border-b">
        Debug Panel
      </p>
      <div className="min-h-0 flex-1 flex flex-col">
        {children}
      </div>
    </div>
  );
}