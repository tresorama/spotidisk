import { createFileRoute } from '@tanstack/react-router';

import { usePlaylist } from '#/hooks/use-playlists';
import type { DerivedPlaylist } from '#/lib/api-client/types';

export const Route = createFileRoute('/playlist/$playlistId')({
  component: RouteComponent,
});

function RouteComponent() {
  const { playlistId } = Route.useParams();
  const queryPlaylist = usePlaylist({ playlistId });

  if (queryPlaylist.isLoading) {
    return <PlaylistLoading />;
  }

  if (queryPlaylist.isError) {
    return <PlaylistError playlistId={playlistId} />;
  }

  if (!queryPlaylist.data) {
    return <PlaylistNotFound playlistId={playlistId} />;
  }

  return <PlaylistView playlist={queryPlaylist.data} />;
}


function PlaylistLoading() {
  return <div>Loading...</div>;
}

function PlaylistNotFound({ playlistId }: { playlistId: string; }) {
  return <div>Playlist {playlistId} not found</div>;
}

function PlaylistError({ playlistId }: { playlistId: string; }) {
  return <div>Error loading playlist {playlistId}</div>;
}

function PlaylistView({ playlist }: { playlist: DerivedPlaylist; }) {
  return (
    <div className="min-h-full flex flex-col">
      <PlaylistHeaderBar playlist={playlist} />
      <PlaylistContent playlist={playlist} />
    </div>
  );
}

function PlaylistHeaderBar({ playlist }: { playlist: DerivedPlaylist; }) {
  return (
    <div className="min-h-16 px-4 flex flex-wrap gap-x-4 gap-y-1 content-center border-b">
      <h1 className="w-full font-semibold">{playlist.name}</h1>
      <p className="text-xs font-light text-muted-foreground">{playlist.spotify_id}</p>
      <p className="text-xs font-light text-muted-foreground">{playlist.spotify_url}</p>
    </div>
  );
}
function PlaylistContent({ playlist }: { playlist: DerivedPlaylist; }) {
  return (
    <div className="min-h-0 flex-1 px-4 py-4 flex flex-col gap-6">
      <div className="flex flex-wrap gap-2">
        <Button
          variant="secondary"
          render={<a href={playlist.spotify_url} target="_blank">Open in Spotify</a>}
        />
        <Button variant="secondary">
          Open download folder (TODO)
        </Button>
      </div>
      <div className="">
        <TablePlaylistTracks playlist={playlist} />
      </div>
    </div>
  );
}

function TablePlaylistTracks({ playlist }: { playlist: DerivedPlaylist; }) {
  return <div>TODO</div>;
}