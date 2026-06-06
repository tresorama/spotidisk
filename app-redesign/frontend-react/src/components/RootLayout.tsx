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
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarProvider,
} from '#/components/ui/sidebar';
import { Button } from '#/components/ui/button';

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
                <SidebarMenu className="mt-2">
                  <SidebarMenuItem>
                    <SidebarMenuSubButton className="text-sm text-muted-foreground">
                      Placeholder item
                    </SidebarMenuSubButton>
                  </SidebarMenuItem>
                </SidebarMenu>
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
