import type { ReactNode } from 'react';
import { Link } from '@tanstack/react-router';

import { AppSidebarHeaderContent } from './sidebar/header-content';
import { AppSidebarNavGroupPlaylists } from './sidebar/nav-group-playlists';
import { AppSidebarNavGroupJobProgress } from './sidebar/nav-group-job-progress';
import { DebugPanel } from './content/debug-panel';
import { AppStatusBar } from './bottom-bar/app-status-bar';

import {
  RootWrapper,
  RootBottomBar,
} from '@/components/ui/root';
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarInset,
  SidebarRail,
  SidebarHeader,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';

interface RootLayoutProps {
  children: ReactNode;
}

export function RootLayout({ children }: RootLayoutProps) {
  return (
    <RootWrapper>
      <AppSidebarWithInset>
        {children}
        <DebugPanel />
      </AppSidebarWithInset>
      <RootBottomBar>
        <AppStatusBar />
      </RootBottomBar>
    </RootWrapper>
  );
}

function AppSidebarWithInset({ children }: { children: React.ReactNode; }) {
  return (
    <SidebarProvider
      defaultOpen={true}
      className={
        "min-h-0 flex-1 relative"
        + " **:data-[slot=sidebar-container]:absolute"
        + " **:data-[slot=sidebar-container]:h-full"
      }
      style={
        {
          "--sidebar-width": "25rem",
        } as React.CSSProperties
      }
    >

      <Sidebar
        role="region"
        aria-label="Sidebar"
        variant="sidebar"
        collapsible="offcanvas"
        className="border-r"
      >

        <SidebarHeader
          role="group"
          aria-label="Sidebar Header"
          className="min-h-16 px-4 py-2 justify-center border-b"
        >
          <AppSidebarHeaderContent />
        </SidebarHeader>

        <SidebarContent
          role="group"
          aria-label="Sidebar Content"
          className="pb-2"
        >
          <AppSidebarNavGroupPlaylists />
          <AppSidebarNavGroupJobProgress />
        </SidebarContent>

        <SidebarFooter
          role="group"
          aria-label="Sidebar Footer"
          className="border-t p-4"
        >
          <div className="flex flex-col gap-2">
            <Button
              variant="outline"
              className="w-full"
              render={<Link to="/add-playlist">Add Playlist</Link>}
              nativeButton={false}
            />
            <Button
              variant="outline"
              className="w-full"
              render={<Link to="/settings">Settings</Link>}
              nativeButton={false}
            />
          </div>
        </SidebarFooter>

        <SidebarRail />

      </Sidebar>


      <SidebarInset
        aria-label="Main Page Content"
        className="min-w-0"
      >
        {children}
      </SidebarInset>

    </SidebarProvider>

  );
}

