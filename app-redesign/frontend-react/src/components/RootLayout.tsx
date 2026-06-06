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
  SidebarMenuItem,
  SidebarMenuSubButton,
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
          <SidebarHeader className="border-b px-6 py-4">
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
              <Button variant="outline" className="w-full" asChild>
                <Link to="/add-playlist">Add Playlist</Link>
              </Button>
              <Button variant="outline" className="w-full" asChild>
                <Link to="/settings">Settings</Link>
              </Button>
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
  const { data: playlists = [], isLoading } = usePlaylists();

  return (
    <SidebarMenu className="mt-2">
      {isLoading ? (
        <SidebarMenuItem>
          <SidebarMenuSubButton className="text-sm text-muted-foreground">
            Loading...
          </SidebarMenuSubButton>
        </SidebarMenuItem>
      ) : playlists.length === 0 ? (
        <SidebarMenuItem>
          <SidebarMenuSubButton className="text-sm text-muted-foreground">
            No playlists
          </SidebarMenuSubButton>
        </SidebarMenuItem>
      ) : (
        playlists.map((playlist) => (
          <SidebarMenuItem key={playlist.id}>
            <SidebarMenuSubButton asChild>
              <Link to={`/playlist/${playlist.id}`}>
                <div className="flex flex-col">
                  <span className="text-sm font-medium">{playlist.name}</span>
                  <span className="text-xs text-muted-foreground">{playlist.total_tracks} tracks</span>
                </div>
              </Link>
            </SidebarMenuSubButton>
          </SidebarMenuItem>
        ))
      )}
    </SidebarMenu>
  );
}