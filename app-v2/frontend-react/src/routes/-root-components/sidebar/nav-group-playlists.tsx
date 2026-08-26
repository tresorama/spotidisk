import { Link, useMatchRoute, useNavigate } from "@tanstack/react-router";
import { EllipsisIcon, TrashIcon } from "lucide-react";

import {
  type PlaylistRaw,
  usePlaylists,
  useMutationPlaylistDeletePlaylist,
} from "#/data";

import { SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarMenuSkeleton } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { DialogConfirmAction, useDialogConfirmAction } from "@/components/ui/dialog.confirm-action";
import { DebugOnlyTooltipData } from "@/components/ui/debug.with-state";

export function AppSidebarNavGroupPlaylists() {
  const queryPlaylists = usePlaylists();

  return (
    <SidebarMenu>
      {queryPlaylists.isLoading ? (
        new Array(12).fill(0).map((_, index) => (
          <SidebarMenuSkeleton
            key={index}
            className="h-9 *:h-[50%] *:self-start first:mt-2"
          />
        ))
      ) : (queryPlaylists.isError || !queryPlaylists.data) ? (
        <SidebarMenuItem className="px-1">
          <Alert variant="destructive">
            <p>Error</p>
            {queryPlaylists.error && <p>{queryPlaylists.error.message}</p>}
          </Alert>
        </SidebarMenuItem>
      ) : queryPlaylists.data.sortedItems.length === 0 ? (
        <SidebarMenuItem className="px-3 pt-2 text-sm text-muted-foreground">
          No playlists
        </SidebarMenuItem>
      ) : (
        queryPlaylists.data.sortedItems.map((playlist) => (
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
    <SidebarMenuItem key={playlist.spotify_id}>
      <SidebarMenuButton
        isActive={isActive}
        render={
          <div className="group/item relative isolate flex-1 flex items-center gap-2">

            <Link
              to="/playlist/$playlistId"
              params={{ playlistId: playlist.spotify_id }}
              className="z-0 absolute inset-0"
            />

            <DebugOnlyTooltipData
              data={playlist}
              className="z-10 relative"
            />

            <span className="text-sm font-medium truncate select-none">
              {playlist.name}
            </span>

            <div className="ml-auto empty:hidden flex items-center gap-[inherit]">

              {!playlist.lastSpotifyFetchDateTimeISO && (
                <Badge>NEW</Badge>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger
                  render={(
                    <Button
                      variant="secondary"
                      size="icon-sm"
                      className="z-10 relative -mr-2 opacity-0 group-hover/item:opacity-100"
                    >
                      <EllipsisIcon />
                    </Button>
                  )}
                />
                <DropdownMenuContent align="end">
                  <DropdownMenuGroup>
                    <DropdownMenuItem
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