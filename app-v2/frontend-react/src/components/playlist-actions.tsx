import { useMutationPlaylistRefetchSpotifySide } from "#/hooks/use-playlists";
import type { DerivedPlaylist } from "#/lib/api-client/types";
import { Button } from "./ui/button";
import { TooltipEasy } from "./ui/tooltip-easy";

export function PlaylistActions({
  playlist
}: {
  playlist: DerivedPlaylist;
}) {

  const mutationPlaylistRefetchSpotifySide = useMutationPlaylistRefetchSpotifySide();

  return (
    <div className="flex flex-wrap justify-between gap-2">
      <div className="flex gap-[inherit]">
        <TooltipEasy tooltipText="Refetch playlist data from Spotify (required when Spotify side is changed and you want to sync to it!)">
          <Button
            onClick={() => mutationPlaylistRefetchSpotifySide.mutate({
              playlistId: playlist.spotify_id,
              playlistName: playlist.name,
            })}
            disabled={mutationPlaylistRefetchSpotifySide.isPending}
            isLoading={mutationPlaylistRefetchSpotifySide.isPending}
            variant="secondary"
          >
            Fetch from Spotify
          </Button>
        </TooltipEasy>
      </div>
      <div className="flex gap-[inherit]">
        <Button
          variant="secondary"
          nativeButton={false}
          render={(
            <a
              href={playlist.spotify_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              View in Spotify
            </a>
          )}
        />
        <Button variant="secondary">
          Open download folder (TODO)
        </Button>
      </div>
    </div>
  );
}