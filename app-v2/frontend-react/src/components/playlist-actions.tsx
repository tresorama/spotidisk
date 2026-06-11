import type { DerivedPlaylist } from "#/lib/api-client/types";
import { Button } from "./ui/button";

export function PlaylistActions({
  playlist
}: {
  playlist: DerivedPlaylist;
}) {
  return (
    <div className="flex flex-wrap justify-between gap-2">
      <div className="flex gap-[inherit]">
        <Button variant="secondary">
          Fetch from Spotify
        </Button>
        <Button variant="secondary">
          Fetch from Spotify
        </Button>
        <Button variant="secondary">
          Fetch from Spotify
        </Button>
        <Button variant="secondary">
          Fetch from Spotify
        </Button>
      </div>
      <div className="flex gap-[inherit]">
        <Button
          variant="secondary"
          render={<a href={playlist.spotify_url} target="_blank">View in Spotify</a>}
        />
        <Button variant="secondary">
          Open download folder (TODO)
        </Button>
      </div>
    </div>
  );
}