import { createFileRoute } from '@tanstack/react-router';

import {
  usePlaylist,
  type DerivedPlaylist,
} from '#/data';

import { PlaylistTopBarContent } from './-components/playlist-top-bar-content';
import { PlaylistActions } from './-components/playlist-actions';
import { PlaylistTracksTable } from './-components/playlist-tracks-table';

import { RootSidebarContentMain, RootSidebarContentTopBar } from '@/components/ui/root';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert } from '@/components/ui/alert';
import { ErrorRenderer } from '#/components/ui/error';

export const Route = createFileRoute('/playlist/$playlistId/')({
  component: RouteComponent,
});

function RouteComponent() {
  const { playlistId } = Route.useParams();

  const queryPlaylist = usePlaylist({ path: { playlist_id: playlistId } });

  if (queryPlaylist.isLoading) {
    return <PlaylistLoading />;
  }

  if (queryPlaylist.isError) {
    return <PlaylistError playlistId={playlistId} error={queryPlaylist.error} />;
  }

  if (!queryPlaylist.data) {
    return <PlaylistNotFound playlistId={playlistId} />;
  }

  return <PlaylistView playlist={queryPlaylist.data} />;
}


function PlaylistLoading() {
  return (
    <>
      <RootSidebarContentTopBar>
        <Skeleton className="w-50 h-8" />
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        {null}
      </RootSidebarContentMain>
    </>
  );
}

function PlaylistNotFound({ playlistId }: { playlistId: string; }) {
  return (
    <>
      <RootSidebarContentTopBar>
        Playlist {playlistId} not found
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        <Alert variant="destructive">
          Playlist {playlistId} not found
        </Alert>
      </RootSidebarContentMain>
    </>
  );
}

function PlaylistError({ playlistId, error }: { playlistId: string; error: Error; }) {
  return (
    <>
      <RootSidebarContentTopBar>
        Error loading playlist {playlistId}
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        <Alert variant="destructive">
          There was an error loading playlist {playlistId}
          <ErrorRenderer error={error} />
        </Alert>
      </RootSidebarContentMain>
    </>
  );
}

function PlaylistView({ playlist }: { playlist: DerivedPlaylist; }) {
  return (
    <>
      <PlaylistHeaderBar playlist={playlist} />
      <PlaylistContent playlist={playlist} />
    </>
  );
}

function PlaylistHeaderBar({ playlist }: { playlist: DerivedPlaylist; }) {
  const queryPlaylist = usePlaylist({ path: { playlist_id: playlist.spotify_id } });

  return (
    <RootSidebarContentTopBar>
      <PlaylistTopBarContent
        playlist={playlist}
        onRefresh={() => queryPlaylist.refetch()}
      />
    </RootSidebarContentTopBar>
  );
}

function PlaylistContent({ playlist }: { playlist: DerivedPlaylist; }) {
  return (
    <RootSidebarContentMain>
      <PlaylistActions playlist={playlist} />
      <div className="min-h-0 flex-1 flex flex-col">
        <PlaylistTracksTable tracks={playlist.tracks} />
      </div>
    </RootSidebarContentMain>
  );
}