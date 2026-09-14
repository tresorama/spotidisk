import { utilsJson } from "#/utils/json";

export function DebugConstants({
  constantsObject
}: {
  constantsObject: Record<string, unknown>;
}) {
  return (
    <pre
      title="debug-panel-constants"
      className="min-h-full p-2 overflow-auto whitespace-pre-wrap text-xs text-muted-foreground"
    >
      {utilsJson.stringify(constantsObject)}
    </pre>
  );
}
