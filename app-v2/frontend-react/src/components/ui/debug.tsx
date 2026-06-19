import { useGlobalDebugVisibility } from "#/state/global.debug-visibility";

export function DebugOnly({ children }: { children: React.ReactNode; }) {
  const debugApi = useGlobalDebugVisibility();
  if (!debugApi.isVisible) {
    return null;
  }
  return <>{children}</>;
}
