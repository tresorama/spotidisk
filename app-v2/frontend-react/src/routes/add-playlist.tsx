import { createFileRoute } from '@tanstack/react-router';
import { RootContentMain, RootContentTopBar } from '@/components/ui/root';

export const Route = createFileRoute('/add-playlist')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <>
      <RootContentTopBar>
        Add playlist
      </RootContentTopBar>
      <RootContentMain>
        {null}
      </RootContentMain>
    </>
  );
}
