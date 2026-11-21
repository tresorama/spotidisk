import { useRef, useState } from "react";
import { Link, useMatchRoute, useNavigate } from "@tanstack/react-router";
import { EllipsisIcon, SearchIcon, TrashIcon, XIcon } from "lucide-react";

import {
  type PlaylistRaw,
  usePlaylists,
  useMutationPlaylistDeletePlaylist,
} from "#/data";

import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarMenuSkeleton } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Input } from "#/components/ui/input";
import { DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { DialogConfirmAction, useDialogConfirmAction } from "@/components/ui/dialog.confirm-action";
import { DebugOnlyTooltipData } from "@/components/ui/debug.with-state";

import { useToggle } from "#/utils/hooks/use-toggle";


export function AppSidebarNavGroupPlaylists() {

  // server state
  const queryPlaylists = usePlaylists();

  // local state
  const searchApi = useSearch();

  return (
    <SidebarGroup
      role="group"
      aria-label="Sidebar Group Playlists"
      className="min-h-0 flex-1"
    >
      <SidebarGroupLabel>
        Playlists
        {queryPlaylists.data && (
          <SearchBox searchApi={searchApi} />
        )}
      </SidebarGroupLabel>
      <SidebarGroupContent
        className="flex-1 overflow-auto no-scrollbar scroll-fade"
      >
        {
          queryPlaylists.isLoading ? (
            <ViewLoading />
          ) : (queryPlaylists.isError || !queryPlaylists.data) ? (
            <ViewError error={queryPlaylists.error} />
          ) : (
            <ViewSuccess
              queryData={queryPlaylists.data}
              searchApi={searchApi}
            />
          )
        }
      </SidebarGroupContent>
    </SidebarGroup>
  );
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
  queryData,
  searchApi,
}: {
  queryData: NonNullable<ReturnType<typeof usePlaylists>['data']>;
  searchApi: ReturnType<typeof useSearch>;
}) {

  // derived state
  const filteredPlaylits = queryData.sortedItems.filter(
    (item) => {
      const name = item.name.toLowerCase();
      const term = searchApi.searchTerm.toLowerCase();
      return name.includes(term);
    }
  );

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
        filteredPlaylits.map(playlist => (
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

// sarch box


function useSearch() {

  // state
  const {
    value: isSearchOpened,
    toggleValue: toggleIsSearchOpened,
  } = useToggle({ initialValue: false });
  const [searchTerm, setSearchTerm] = useState('');

  // derived state
  const searchTermIsDirty = searchTerm !== '';

  return {
    // state
    isSearchOpened,
    searchTerm,
    searchTermIsDirty,
    // actions
    toggleIsSearchOpened,
    setSearchTerm,
  };
}


function SearchBox({
  searchApi,
}: {
  searchApi: ReturnType<typeof useSearch>;
}) {

  // local state
  const refElInput = useRef<HTMLInputElement | null>(null);
  const focusInput = () => {
    setTimeout(() => { refElInput.current?.focus(); }, 100);
  };

  // actions

  /** Toggle the enabled state of the search box, and focus th input if needed */
  const handleTogglerClick = () => {
    searchApi.toggleIsSearchOpened();
    if (!searchApi.isSearchOpened) focusInput();
  };

  /** <input> onChange handler */
  const handleInputChange: React.ComponentProps<'input'>['onChange'] = (e) => {
    searchApi.setSearchTerm(e.currentTarget.value);
  };

  /** clear search term click handler */
  const handleClearTextClick = () => {
    searchApi.setSearchTerm('');
    focusInput();
  };


  if (!searchApi.isSearchOpened) {
    return (
      <Button
        onClick={handleTogglerClick}
        variant="ghost"
        size={searchApi.searchTermIsDirty ? "xs" : "icon-xs"}
        className="ml-auto"
      >
        {searchApi.searchTerm}
        <SearchIcon />
      </Button>
    );
  }

  return (
    <div className="relative ml-auto flex items-center">
      <Input
        ref={refElInput}
        value={searchApi.searchTerm}
        onChange={handleInputChange}
        className="h-6 px-6 pb-1.5"
      />
      <Button
        onClick={handleTogglerClick}
        variant="ghost"
        size="icon-xs"
        className="absolute left-2 size-3"
      >
        <SearchIcon />
      </Button>
      {searchApi.searchTerm && (
        <Button
          onClick={handleClearTextClick}
          variant="ghost"
          size="icon-xs"
          className="absolute right-2 size-3"
        >
          <XIcon />
        </Button>
      )}
    </div>
  );
}