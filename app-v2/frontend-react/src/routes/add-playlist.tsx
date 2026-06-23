import { createFileRoute } from '@tanstack/react-router';
import z from 'zod';
import { PlusIcon } from 'lucide-react';

import { RootContentMain, RootContentTopBar } from '@/components/ui/root';
import { Field, FieldDescription, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/sonner';
import { useAddPlaylist } from '#/data/use-playlists';

export const Route = createFileRoute('/add-playlist')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <>
      <RootContentTopBar>
        <h1 className="font-semibold">
          Add playlist
        </h1>
      </RootContentTopBar>
      <RootContentMain>
        <FormAddPlaylist />
      </RootContentMain>
    </>
  );
}


const schemaForm = z.object({
  playlistSpotifyUrl: z.url(),
});


function FormAddPlaylist() {
  const mutationAddPlaylist = useAddPlaylist();

  const handleFormSubmit: React.ComponentProps<'form'>['onSubmit'] = (e) => {
    e.preventDefault();

    const dataRaw = Object.fromEntries(new FormData(e.currentTarget).entries());
    const dataParsed = schemaForm.safeParse(dataRaw);
    if (!dataParsed.success) {
      toast.error('Invalid form data, please fix and try again.');
      return;
    }

    const { data } = dataParsed;
    mutationAddPlaylist.mutate(data);
  };

  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={handleFormSubmit}
    >
      <Field>
        <FieldLabel htmlFor="playlistSpotifyUrl">
          Playlist Spotify URL
        </FieldLabel>
        <Input
          type="url"
          id="playlistSpotifyUrl"
          name="playlistSpotifyUrl"
          placeholder="Playlist URL from Spotify"
          autoComplete="off"
        />
        <FieldDescription>
          You should get from Spotify - Playlist - Share - Copy link
        </FieldDescription>
      </Field>
      <Field orientation="horizontal">
        <Button
          type="submit"
          className="leading-none"
          disabled={mutationAddPlaylist.isPending}
          isLoading={mutationAddPlaylist.isPending}
        >
          <PlusIcon />
          Add
        </Button>
      </Field>
    </form>
  );
}