import { createFileRoute } from '@tanstack/react-router';

import {
  usePlaylist,
  type DerivedPlaylist,
} from '#/data';

import { PlaylistTitle } from './-components/playlist-title';
import { PlaylistTopBarContent } from './-components/playlist-top-bar-content';
import { PlaylistActions } from './-components/playlist-actions';
import { PlaylistTracksTable } from './-components/playlist-tracks-table';

import { RootSidebarContentMain, RootSidebarContentTopBar } from '@/components/ui/root';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertTitle } from '@/components/ui/alert';
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

  if (queryPlaylist.isError || !queryPlaylist.data) {
    return <PlaylistError playlistId={playlistId} error={queryPlaylist.error} />;
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

function PlaylistError({
  playlistId,
  error
}: {
  playlistId: string;
  error: Error | null;
}) {
  return (
    <>
      <RootSidebarContentTopBar>
        <PlaylistTitle
          playlistId={playlistId}
          playlist={null}
        />
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        <Alert
          aria-label={`Error loading playlist`}
          data-playlist-id={playlistId}
          variant="destructive"
        >
          <AlertTitle>
            Error loading playlist
          </AlertTitle>
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
      <PlaylistActions
        playlist={playlist}
        className="shrink-0"
      />
      <PlaylistTracksTable
        tracks={playlist.tracks}
        playlistId={playlist.spotify_id}
        className="min-h-0 flex-1"
      />
    </RootSidebarContentMain>
  );
}