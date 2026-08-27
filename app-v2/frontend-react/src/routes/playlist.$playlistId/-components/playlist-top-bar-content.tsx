import { Button } from "#/components/ui/button";
import { DebugOnlyTooltipData } from "#/components/ui/debug.with-state";
import type { DerivedPlaylist } from "#/data";

export function PlaylistTopBarContent({
  playlist,
  onRefresh,
}: {
  playlist: DerivedPlaylist;
  onRefresh: () => void;
}) {

  return (
    <>
      <h1 className="font-semibold">
        {playlist.name}
      </h1>
      <DebugOnlyTooltipData
        data={playlist}
      />
      <Button
        variant="secondary"
        onClick={() => onRefresh()}
        className="ml-auto"
      >
        Refresh
      </Button>
    </>
  );
}