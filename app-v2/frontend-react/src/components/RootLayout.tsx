import type { ReactNode } from 'react';
import { Link } from '@tanstack/react-router';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from '#/components/ui/sidebar';
import { Button } from '#/components/ui/button';
import { usePlaylists } from '#/hooks/use-playlists';

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen">

        <Sidebar className="border-r">
          <SidebarHeader className="min-h-16 border-b px-6 py-4">
            <h1 className="text-xl font-semibold">sunnify</h1>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>
                Playlists
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <NavGroupPlaylists />
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter className="border-t p-4">
            <div className="flex flex-col gap-2">
              <Button
                variant="outline"
                className="w-full"
                render={<Link to="/add-playlist">Add Playlist</Link>}
              />
              <Button
                variant="outline"
                className="w-full"
                render={<Link to="/settings">Settings</Link>}
              />
            </div>
          </SidebarFooter>
        </Sidebar>

        <main className="flex-1 overflow-auto bg-background">
          {children}
        </main>
      </div>
    </SidebarProvider>
  );
}


function NavGroupPlaylists() {
  const { data: playlists, isLoading, isError, error } = usePlaylists();

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
        playlists.map((playlist) => (
          <SidebarMenuItem key={playlist.spotify_id}>
            <SidebarMenuButton
              className="h-12"
              render={
                <Link to="/playlist/$playlistId" params={{ playlistId: playlist.spotify_id }}>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium truncate">{playlist.name}</span>
                    <span className="text-xs text-muted-foreground">{playlist.tracks_count} tracks</span>
                  </div>
                </Link>
              }
            />
          </SidebarMenuItem>
        ))
      )}
    </SidebarMenu>
  );
}