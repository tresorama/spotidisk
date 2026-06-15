import { SiSpotify } from "@icons-pack/react-simple-icons";
import { HardDriveIcon } from "lucide-react";

import type { DerivedPlaylist } from "@/lib/api-client/types";
import { useMutationPlaylistRefetchSpotifySide } from "@/hooks/use-playlists";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TooltipEasy } from "@/components/ui/tooltip-easy";

export function PlaylistActions({
  playlist
}: {
  playlist: DerivedPlaylist;
}) {

  const mutationPlaylistRefetchSpotifySide = useMutationPlaylistRefetchSpotifySide();

  return (
    <div className="px-3 py-3 flex flex-wrap justify-between border rounded-md">

      <div className="flex-1 flex flex-wrap gap-1 items-center">
        <p className="w-full font-medium text-sm">Spotify</p>
        <TooltipEasy tooltipText="Spotify Playlist ID">
          <Badge variant="outline">{playlist.spotify_id}</Badge>
        </TooltipEasy>
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
            <SiSpotify />
            Fetch
          </Button>
        </TooltipEasy>
        <TooltipEasy tooltipText="View the playlist on Spotify in a new tab">
          <Button
            variant="secondary"
            nativeButton={false}
            render={(
              <a
                href={playlist.spotify_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <SiSpotify />
                View
              </a>
            )}
          />
        </TooltipEasy>
      </div>

      <div className="flex-1 flex flex-wrap gap-1 items-center">
        <p className="w-full font-medium text-sm">Disk</p>
        <Badge variant="outline">{playlist.disk_path}</Badge>
        <TooltipEasy tooltipText="Open the playlist folder on your computer">
          <Button variant="secondary">
            <HardDriveIcon />
            Open
          </Button>
        </TooltipEasy>
      </div>

    </div>
  );
}