import { Link } from "@tanstack/react-router";
import { DebugPanelToggler } from "../content/debug-panel";
import { SidebarTrigger } from "#/components/ui/sidebar";

export function AppSidebarHeaderContent() {
  return (
    <div
      className="flex items-center gap-4 *:last:ml-auto"
    >
      <SidebarTrigger
        variant="outline"
        size="icon"
      />
      <Link
        to="/"
        className="text-lg font-semibold"
      >
        SpotiDisk
      </Link>
      <DebugPanelToggler />
    </div>
  );
}