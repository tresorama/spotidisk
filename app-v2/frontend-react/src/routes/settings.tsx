import { createFileRoute } from '@tanstack/react-router';
import { RootContentMain, RootContentTopBar } from '@/components/ui/root';

export const Route = createFileRoute('/settings')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <>
      <RootContentTopBar>
        Settings
      </RootContentTopBar>
      <RootContentMain>
        {null}
      </RootContentMain>
    </>
  );
}
