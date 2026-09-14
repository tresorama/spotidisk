import { Link, useMatchRoute, useNavigate } from "@tanstack/react-router";
import { EllipsisIcon, TrashIcon } from "lucide-react";

import {
  type PlaylistRaw,
  usePlaylists,
  useMutationPlaylistDeletePlaylist,
} from "#/data";

import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarMenuSkeleton } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { DialogConfirmAction, useDialogConfirmAction } from "@/components/ui/dialog.confirm-action";
import { DebugOnlyTooltipData } from "@/components/ui/debug.with-state";


export function AppSidebarNavGroupPlaylists() {
  return (
    <SidebarGroup
      role="group"
      aria-label="Sidebar Group Playlists"
      className="min-h-0 flex-1"
    >
      <SidebarGroupLabel>
        Playlists
      </SidebarGroupLabel>
      <SidebarGroupContent
        className="flex-1 overflow-auto no-scrollbar scroll-fade"
      >
        <GroupContent />
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

function GroupContent() {
  const queryPlaylists = usePlaylists();
  if (queryPlaylists.isLoading) {
    return <ViewLoading />;
  }

  if (queryPlaylists.isError || !queryPlaylists.data) {
    return <ViewError error={queryPlaylists.error} />;
  }

  return <ViewSuccess queryData={queryPlaylists.data} />;
}

function ViewLoading() {
  return (
    <SidebarMenu>
      {new Array(12).fill(0).map((_, index) => (
        <SidebarMenuSkeleton
          key={index}
          className="h-9 *:h-[50%] *:self-start first:mt-2"
        />
      ))}
    </SidebarMenu>
  );
}

function ViewError({ error }: { error: Error | null; }) {
  return (
    <SidebarMenu>
      <SidebarMenuItem className="px-1">
        <Alert variant="destructive">
          <p>Error</p>
          {error && <p>{error.message}</p>}
        </Alert>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}

function ViewSuccess({
  queryData
}: {
  queryData: NonNullable<ReturnType<typeof usePlaylists>['data']>;
}) {

  return (
    <SidebarMenu
      aria-label="Sidebar Group Playlists List"
      data-items-count={queryData.sortedItems.length}
    >
      {queryData.sortedItems.length === 0 ? (
        <SidebarMenuItem
          aria-label="No playlists"
          className="px-3 pt-2 text-sm text-muted-foreground"
        >
          No playlists
        </SidebarMenuItem>
      ) : (
        queryData.sortedItems.map(playlist => (
          <SidebarItemPlaylist
            key={playlist.spotify_id}
            playlist={playlist}
          />
        ))
      )}
    </SidebarMenu>
  );
}


function SidebarItemPlaylist({
  playlist,
}: {
  playlist: PlaylistRaw;
}) {

  // data
  const mutationDeletePlaylist = useMutationPlaylistDeletePlaylist();

  // router
  const matchRoute = useMatchRoute();
  const navigate = useNavigate();

  // local state
  const dialogStateDeletePlaylist = useDialogConfirmAction();

  // derived
  const isActive = Boolean(matchRoute({
    to: "/playlist/$playlistId",
    params: { playlistId: playlist.spotify_id },
    fuzzy: true,
    // fuzzy: !item.exact 
  }));

  // events
  const handleConfirmedDeletePlaylist = async () => {
    if (isActive) {
      navigate({ to: "/" });
    }

    await mutationDeletePlaylist.mutateAsync({
      path: {
        playlist_id: playlist.spotify_id,
      }
    });

  };

  return (
    <SidebarMenuItem
      key={playlist.spotify_id}
      aria-label={playlist.name}
      data-playlist-id={playlist.spotify_id}
      data-is-active={isActive}
    >
      <SidebarMenuButton
        isActive={isActive}
        render={
          <div className="group/item relative isolate flex-1 flex items-center gap-2">

            <Link
              aria-label="Go to Playlist page"
              to="/playlist/$playlistId"
              params={{ playlistId: playlist.spotify_id }}
              className="z-0 absolute inset-0"
            />

            <DebugOnlyTooltipData
              data={playlist}
              className="z-10 relative"
            />

            <span
              aria-label="Playlist Name"
              className="text-sm font-medium truncate select-none"
            >
              {playlist.name}
            </span>

            <div className="ml-auto empty:hidden flex items-center gap-[inherit]">

              {!playlist.lastSpotifyFetchDateTimeISO && (
                <Badge
                  aria-label="Playlist is new"
                >
                  NEW
                </Badge>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger
                  render={(
                    <Button
                      aria-label="Playlist Options"
                      variant="secondary"
                      size="icon-sm"
                      className="z-10 relative -mr-2 opacity-0 group-hover/item:opacity-100"
                    >
                      <EllipsisIcon />
                    </Button>
                  )}
                />
                <DropdownMenuContent
                  align="end"
                >
                  <DropdownMenuGroup>
                    <DropdownMenuItem
                      aria-label="Delete Playlist"
                      onClick={() => dialogStateDeletePlaylist.setIsOpen(true)}
                      variant="destructive"
                    >
                      <TrashIcon />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuGroup>
                </DropdownMenuContent>
              </DropdownMenu>

            </div>

            <DialogConfirmAction
              dialogState={dialogStateDeletePlaylist}
              onConfirm={handleConfirmedDeletePlaylist}
              title="Are you sure to delete this playlist?"
              description="This action cannot be undone and cannot be reversed. Already downloaded tracks will not be deleted from your disk."
              buttonCancelText="Keep it"
              buttonConfirmText="Delete Playlist"
            />

          </div>
        }
      />
    </SidebarMenuItem>
  );

}