import { Link, useMatchRoute } from "@tanstack/react-router";

import { usePlaylists } from "#/data/use-playlists";

import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "#/components/ui/sidebar";

export function NavGroupPlaylists() {
  const { data: playlists, isLoading, isError, error } = usePlaylists();
  const matchRoute = useMatchRoute();

  return (
    <SidebarMenu>
      {isLoading ? (
        <SidebarMenuItem className="px-3 text-xs text-muted-foreground">
          Loading...
        </SidebarMenuItem>
      ) : (isError || !playlists) ? (
        <SidebarMenuItem className="px-3 text-xs text-muted-foreground">
          <p>Error</p>
          {error && <p>{error.message}</p>}
        </SidebarMenuItem>
      ) : playlists.length === 0 ? (
        <SidebarMenuItem className="text-sm text-muted-foreground">
          No playlists
        </SidebarMenuItem>
      ) : (
        playlists.map((playlist) => {
          const isActive = Boolean(matchRoute({
            to: "/playlist/$playlistId",
            params: { playlistId: playlist.spotify_id },
            fuzzy: true,
            // fuzzy: !item.exact 
          }));
          return (
            <SidebarMenuItem key={playlist.spotify_id}>
              <SidebarMenuButton
                className="h-12"
                isActive={isActive}
                render={
                  <Link
                    to="/playlist/$playlistId"
                    params={{ playlistId: playlist.spotify_id }}
                  >
                    <div className="flex flex-col">
                      <span className="text-sm font-medium truncate">{playlist.name}</span>
                      <span className="text-xs text-muted-foreground">{playlist.tracks_count} tracks</span>
                    </div>
                  </Link>
                }
              />
            </SidebarMenuItem>
          );
        })
      )}
    </SidebarMenu>
  );
}
