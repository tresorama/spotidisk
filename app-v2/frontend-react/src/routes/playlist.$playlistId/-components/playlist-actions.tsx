import { useRef } from "react";
import { SiSpotify, SiYoutube } from "@icons-pack/react-simple-icons";
import { HardDriveIcon, PencilIcon } from "lucide-react";

import {
  type DerivedPlaylist,
  useMutationPlaylistUpdatePlaylist,
  useMutationPlaylistRefetchSpotifySide,
  useMutationPlaylistDownloadAllTracks,
  useMutationPlaylistFindTrackYoutubeUrlAllTracks,
  useMutationUtilsDiskRevealInFinder,
} from "#/data";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TooltipEasy } from "@/components/ui/tooltip-easy";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Field, FieldContent, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useToggle } from "#/utils/hooks/use-toggle";

export function PlaylistActions({
  playlist
}: {
  playlist: DerivedPlaylist;
}) {

  const mutationPlaylistUpdatePlaylist = useMutationPlaylistUpdatePlaylist();
  const mutationPlaylistRefetchSpotifySide = useMutationPlaylistRefetchSpotifySide();
  const mutationUtilsDiskRevealInFinder = useMutationUtilsDiskRevealInFinder();
  const mutationPlaylistDownloadAllTracks = useMutationPlaylistDownloadAllTracks();
  const mutationPlaylistAutoSearchYoutubeUrl = useMutationPlaylistFindTrackYoutubeUrlAllTracks();

  const dialogSetPlaylistDirNameVisibility = useToggle({ initialValue: false });

  return (
    <div className="flex flex-wrap justify-between border rounded-md overflow-hidden">

      <Block title="Spotify">
        <BlockRow>
          <TooltipEasy tooltipText="Spotify Playlist Name (updated during Fetch)">
            <Badge variant="outline">
              {playlist.name}
            </Badge>
          </TooltipEasy>
          <TooltipEasy tooltipText="Spotify Playlist ID">
            <Badge variant="outline">
              {playlist.spotify_id}
            </Badge>
          </TooltipEasy>
        </BlockRow>
        <BlockRow>
          <TooltipEasy tooltipText="Refetch playlist data from Spotify (required when Spotify side is changed and you want to sync to it!)">
            <Button
              onClick={() => {
                mutationPlaylistRefetchSpotifySide.mutate({
                  path: { playlist_id: playlist.spotify_id }
                });
              }}
              disabled={mutationPlaylistRefetchSpotifySide.isPending}
              isLoading={mutationPlaylistRefetchSpotifySide.isPending}
              variant="secondary"
            >
              <SiSpotify />
              Fetch
            </Button>
          </TooltipEasy>
          <TooltipEasy tooltipText="View the playlist on Spotify in a new tab">
            <Button
              variant="secondary"
              nativeButton={false}
              render={(
                <a
                  href={playlist.spotify_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <SiSpotify />
                  View
                </a>
              )}
            />
          </TooltipEasy>
        </BlockRow>
      </Block>

      <Block title="Youtube">
        <BlockRow>
          <TooltipEasy tooltipText="Do Youtube 'Auto-Search URL' for all tracks that don't have one in this playlist">
            <Button
              onClick={() => {
                mutationPlaylistAutoSearchYoutubeUrl.mutate({
                  path: { playlist_id: playlist.spotify_id, }
                });
              }}
              disabled={mutationPlaylistAutoSearchYoutubeUrl.isPending}
              isLoading={mutationPlaylistAutoSearchYoutubeUrl.isPending}
              variant="secondary"
            >
              <SiYoutube />
              Auto Search URL
            </Button>
          </TooltipEasy>
        </BlockRow>
      </Block>

      <Block title="Disk">
        <BlockRow>
          <TooltipEasy tooltipText="The path of this playlist on your computer, where the tracks are stored">
            <Badge variant="outline">
              {playlist.disk_path}
            </Badge>
          </TooltipEasy>
        </BlockRow>
        <BlockRow>
          <Dialog
            open={dialogSetPlaylistDirNameVisibility.value}
            onOpenChange={dialogSetPlaylistDirNameVisibility.setValue}
          >
            <TooltipEasy tooltipText="Update the directory name of the playlist folder on your computer">
              <DialogTrigger
                render={(
                  <Button
                    isLoading={mutationPlaylistUpdatePlaylist.isPending}
                    variant="secondary"
                  >
                    <PencilIcon />
                    Rename
                  </Button>
                )}
              />
            </TooltipEasy>
            <DialogContentSetPlaylistDirName
              currentDirName={playlist.directory_name_resolved}
              currentSpotifyName={playlist.name}
              onConfirmed={newDirName => {
                if (!newDirName) return;
                mutationPlaylistUpdatePlaylist.mutate({
                  body: {
                    playlist_id: playlist.spotify_id,
                    directory_name: newDirName,
                  }
                });
                dialogSetPlaylistDirNameVisibility.setValue(false);
              }}
            />
          </Dialog>

          <TooltipEasy tooltipText="Open the playlist folder on your computer">
            <Button
              onClick={() => {
                mutationUtilsDiskRevealInFinder.mutate({
                  body: { path: playlist.disk_path },
                });
              }}
              disabled={mutationUtilsDiskRevealInFinder.isPending}
              isLoading={mutationUtilsDiskRevealInFinder.isPending}
              variant="secondary"
            >
              <HardDriveIcon />
              Open
            </Button>
          </TooltipEasy>
          <TooltipEasy tooltipText="Download all missing tracks of this playlist. Only tracks that have Youtube linke and are not yet downloaded will be downloaded!">
            <Button
              onClick={() => {
                mutationPlaylistDownloadAllTracks.mutate({
                  path: { playlist_id: playlist.spotify_id },
                });
              }}
              disabled={mutationPlaylistDownloadAllTracks.isPending}
              isLoading={mutationPlaylistDownloadAllTracks.isPending}
              variant="secondary"
            >
              <HardDriveIcon />
              Download All
            </Button>
          </TooltipEasy>
        </BlockRow>
      </Block>

    </div>
  );
}

function DialogContentSetPlaylistDirName({
  currentDirName,
  currentSpotifyName,
  onConfirmed,
}: {
  currentDirName?: string | null;
  currentSpotifyName: string;
  onConfirmed: (newDirName: string | null) => void;
}) {

  const refInput = useRef<HTMLInputElement>(null);

  const handleSubmit = () => onConfirmed(refInput.current?.value ?? null);
  const handleUseSpotifyNameClick = () => {
    if (!refInput.current) return;
    refInput.current.value = currentSpotifyName;
  };

  return (
    <DialogContent className="w-240 sm:max-w-[80dvw]">
      <DialogHeader>
        <DialogTitle>Rename the playlist folder on your computer</DialogTitle>
        <DialogDescription>
          This action will rename the playlist folder on your computer
        </DialogDescription>
      </DialogHeader>
      <Field>
        <FieldLabel>
          Directory Name
          <Button
            onClick={handleUseSpotifyNameClick}
            variant="link"
          >
            Use Spotify Name {`"${currentSpotifyName}"`}
          </Button>
        </FieldLabel>
        <FieldContent>
          <Input
            ref={refInput}
            defaultValue={currentDirName ?? ''}
          />
        </FieldContent>
      </Field>
      <Field orientation="horizontal">
        <DialogClose
          render={(
            <Button variant="secondary">
              Cancel
            </Button>
          )}
        />
        <Button
          onClick={handleSubmit}
          variant="default"
        >
          Update
        </Button>
      </Field>
    </DialogContent>
  );
}

// ui

function Block({
  title,
  children
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex-1 flex flex-col not-first:border-l">
      <div className="w-full p-3 bg-muted/50 pr-8">
        <p className="w-full font-medium text-sm">
          {title}
        </p>
      </div>
      <div className="flex-1 px-3 pt-4 pb-3 flex flex-col justify-end gap-3">
        {children}
      </div>
    </div>
  );
}

function BlockRow({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex gap-2 justify-start">
      {children}
    </div>
  );
}
