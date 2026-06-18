
import { useGlobalEventsLogs, type EventItem } from "#/state/global.backend-events";
import { utilsJson } from "#/utils/json";

export function EventsLogs() {
  const eventsLogs = useGlobalEventsLogs();

  return (
    <UIList>
      {eventsLogs.map((event, index) => <UIItem key={index} event={event} />)}
    </UIList>
  );
}



// ui

function UIList({ children }: { children: React.ReactNode; }) {
  return (
    <div className="h-full overflow-auto flex flex-col-reverse">
      {children}
    </div>
  );
}


function UIItem({ event }: { event: EventItem; }) {
  const text = utilsJson.stringify(event.data);
  return (
    <div className="min-w-full px-2 py-2 border-b text-xs text-muted-foreground whitespace-nowrap">
      {text}
    </div>
  );
}