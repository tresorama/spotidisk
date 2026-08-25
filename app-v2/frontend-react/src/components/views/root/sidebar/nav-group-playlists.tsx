import { Link, useMatchRoute } from "@tanstack/react-router";

import { usePlaylists } from "#/data";

import { SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarMenuSkeleton } from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { DebugOnlyTooltipData } from "#/components/ui/debug.with-state";

export function AppSidebarNavGroupPlaylists() {
  const queryPlaylists = usePlaylists();
  const matchRoute = useMatchRoute();

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
        queryPlaylists.data.sortedItems.map((playlist) => {
          const isActive = Boolean(matchRoute({
            to: "/playlist/$playlistId",
            params: { playlistId: playlist.spotify_id },
            fuzzy: true,
            // fuzzy: !item.exact 
          }));
          return (
            <SidebarMenuItem key={playlist.spotify_id}>
              <SidebarMenuButton
                isActive={isActive}
                render={
                  <Link
                    to="/playlist/$playlistId"
                    params={{ playlistId: playlist.spotify_id }}
                  >
                    <div className="flex-1 flex items-center gap-2">
                      <DebugOnlyTooltipData data={playlist} />
                      <span className="text-sm font-medium truncate">{playlist.name}</span>
                      {!playlist.lastSpotifyFetchDateTimeISO && (
                        <Badge className="ml-auto">NEW</Badge>
                      )}
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
