import React, { useRef } from "react";
import { SiSpotify, SiYoutube } from "@icons-pack/react-simple-icons";
import { HardDriveIcon, PencilIcon } from "lucide-react";

import {
  type DerivedPlaylist,
  useMutationPlaylistUpdatePlaylist,
  useMutationPlaylistRefetchSpotifySide,
  useMutationPlaylistDownloadAllTracks,
  useMutationPlaylistFindTrackYoutubeUrlAllTracks,
  useMutationUtilsDiskRevealInFinder,
  useMutationPlaylistDeleteOrphanTracks,
} from "#/data";

import { cn } from "#/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TooltipEasy } from "@/components/ui/tooltip-easy";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Field, FieldGroup, FieldLabel, FieldSet } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useToggle } from "#/utils/hooks/use-toggle";

export function PlaylistActions({
  playlist,
  className,
}: {
  playlist: DerivedPlaylist;
  className?: React.ComponentProps<"div">["className"];
}) {
  return (
    <BlockWrapper
      role="group"
      aria-label="Playlist Actions"
      data-playlist-id={playlist.spotify_id}
      className={className}
    >
      <BlockSpotify playlist={playlist} />
      <BlockYoutube playlist={playlist} />
      <BlockDisk playlist={playlist} />
    </BlockWrapper>
  );
}

function BlockSpotify({
  playlist,
}: {
  playlist: DerivedPlaylist;
}) {

  const mutationPlaylistRefetchSpotifySide = useMutationPlaylistRefetchSpotifySide();

  return (
    <Block
      title="Spotify"
      role="group"
      aria-label="Playlist Actions Spotify"
    >
      <BlockRow>
        <TooltipEasy tooltipText="Spotify Playlist Name (updated during Fetch)">
          <Badge
            aria-label="Spotify Playlist Name"
            variant="outline"
          >
            {playlist.name}
          </Badge>
        </TooltipEasy>
        <TooltipEasy tooltipText="Spotify Playlist ID">
          <Badge
            aria-label="Spotify Playlist ID"
            variant="outline"
          >
            {playlist.spotify_id}
          </Badge>
        </TooltipEasy>
      </BlockRow>
      <BlockRow>
        <TooltipEasy tooltipText="Refetch playlist data from Spotify (required when Spotify side is changed and you want to sync to it!)">
          <Button
            aria-label="Refetch playlist data from Spotify"
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
            aria-label="View the playlist on Spotify in a new tab"
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
  );
}

function BlockYoutube({
  playlist,
}: {
  playlist: DerivedPlaylist;
}) {

  const mutationPlaylistAutoSearchYoutubeUrl = useMutationPlaylistFindTrackYoutubeUrlAllTracks();

  return (
    <Block
      title="Youtube"
      role="group"
      aria-label="Playlist Actions Youtube"
    >
      <BlockRow>

        <TooltipEasy tooltipText="Do Youtube 'Auto-Search URL' for all tracks that don't have one in this playlist">
          <Button
            aria-label="Run Youtube 'Auto-Search URL' for all tracks"
            variant="secondary"
            disabled={mutationPlaylistAutoSearchYoutubeUrl.isPending}
            isLoading={mutationPlaylistAutoSearchYoutubeUrl.isPending}
            onClick={() => {
              mutationPlaylistAutoSearchYoutubeUrl.mutate({
                path: { playlist_id: playlist.spotify_id, }
              });
            }}
          >
            <SiYoutube />
            Auto Search URL
          </Button>
        </TooltipEasy>

      </BlockRow>
    </Block>
  );
}

function BlockDisk({
  playlist,
}: {
  playlist: DerivedPlaylist;
}) {

  const mutationUtilsDiskRevealInFinder = useMutationUtilsDiskRevealInFinder();
  const mutationPlaylistDownloadAllTracks = useMutationPlaylistDownloadAllTracks();
  const mutationPlaylistDeleteOrphanTracks = useMutationPlaylistDeleteOrphanTracks();

  const dialogSetPlaylistDirNameVisibility = useToggle({ initialValue: false });

  const diskDirName = playlist.directory_name_resolved;
  const diskPathParent = playlist.disk_path.split("/").slice(0, -1).join("/");

  return (
    <Block
      title="Disk"
      role="group"
      aria-label="Playlist Actions Disk"
    >
      <BlockRow>

        <TooltipEasy tooltipText="The path of this playlist on your computer, where the tracks are stored">
          <span className="flex gap-2 items-center">
            <Badge
              aria-label="Playlist Disk Path Parent"
              variant="outline"
            >
              {diskPathParent}
            </Badge>
            {"/"}
            <Badge
              aria-label="Playlist Disk Directory Name"
              variant="outline"
            >
              {diskDirName}
            </Badge>
          </span>
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
                  aria-label="Update the directory name of the playlist folder on your computer"
                  variant="secondary"
                >
                  <PencilIcon />
                  Rename
                </Button>
              )}
            />
          </TooltipEasy>
          <DialogContentSetPlaylistDirName
            playlistId={playlist.spotify_id}
            currentDirName={playlist.directory_name_resolved}
            currentSpotifyName={playlist.name}
            onSubmitDone={() => {
              dialogSetPlaylistDirNameVisibility.setValue(false);
            }}
          />
        </Dialog>

        <TooltipEasy tooltipText="Open the playlist folder on your computer">
          <Button
            aria-label="Open playlist folder on your computer"
            variant="secondary"
            disabled={mutationUtilsDiskRevealInFinder.isPending}
            isLoading={mutationUtilsDiskRevealInFinder.isPending}
            onClick={() => {
              mutationUtilsDiskRevealInFinder.mutate({
                body: { path: playlist.disk_path },
              });
            }}
          >
            <HardDriveIcon />
            Open
          </Button>
        </TooltipEasy>

        <TooltipEasy tooltipText="Download all missing tracks of this playlist. Only tracks that have Youtube linke and are not yet downloaded will be downloaded!">
          <Button
            aria-label="Download all missing tracks of this playlist"
            variant="secondary"
            disabled={mutationPlaylistDownloadAllTracks.isPending}
            isLoading={mutationPlaylistDownloadAllTracks.isPending}
            onClick={() => {
              mutationPlaylistDownloadAllTracks.mutate({
                path: { playlist_id: playlist.spotify_id },
              });
            }}
          >
            <HardDriveIcon />
            Download All
          </Button>
        </TooltipEasy>

        <TooltipEasy tooltipText="Delete orphan files in the playlist folder. If you reordered the playlist tracks on Spotify, files of your disk are not correct anymore. This action will delete every file that hasn't a corresponding playlist track fil name.">
          <Button
            aria-label="Delete orphan files in the playlist folder"
            variant="secondary"
            disabled={mutationPlaylistDeleteOrphanTracks.isPending}
            isLoading={mutationPlaylistDeleteOrphanTracks.isPending}
            onClick={() => {
              mutationPlaylistDeleteOrphanTracks.mutate({
                path: { playlist_id: playlist.spotify_id },
              });
            }}
          >
            <HardDriveIcon />
            Delete Orphans
          </Button>
        </TooltipEasy>

      </BlockRow>
    </Block>
  );
}

function DialogContentSetPlaylistDirName({
  playlistId,
  currentDirName,
  currentSpotifyName,
  onSubmitDone,
}: {
  playlistId: DerivedPlaylist['spotify_id'],
  currentDirName?: string | null;
  currentSpotifyName: string;
  onSubmitDone: () => void;
}) {

  // data
  const mutationPlaylistUpdatePlaylist = useMutationPlaylistUpdatePlaylist();

  // local state
  const refInput = useRef<HTMLInputElement>(null);
  const a11yMap = {
    newDiskDirNameInput: {
      id: 'newDiskDirNameInput',
    }
  };

  // events
  const handleSubmit: React.ComponentProps<"form">["onSubmit"] = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    // get form values
    const newDirName = refInput.current?.value ?? null;
    if (!newDirName) return;

    // call server
    await mutationPlaylistUpdatePlaylist.mutateAsync({
      body: {
        playlist_id: playlistId,
        directory_name: newDirName,
      }
    });

    onSubmitDone();
  };

  const handleUseSpotifyNameClick = () => {
    if (!refInput.current) return;
    refInput.current.value = currentSpotifyName;
  };

  return (
    <DialogContent className="w-240 sm:max-w-[80dvw]">
      <DialogHeader>
        <DialogTitle>
          Rename the playlist folder on your computer
        </DialogTitle>
        <DialogDescription>
          This action will rename the playlist folder on your computer
        </DialogDescription>
      </DialogHeader>

      <form
        aria-label="Update the directory name of the playlist folder on your computer"
        onSubmit={handleSubmit}
      >
        <FieldSet>

          <FieldGroup>

            <Field>
              <FieldLabel htmlFor={a11yMap.newDiskDirNameInput.id}>
                Directory Name
                <Button
                  onClick={handleUseSpotifyNameClick}
                  variant="link"
                >
                  Use Spotify Name {`"${currentSpotifyName}"`}
                </Button>
              </FieldLabel>
              <Input
                ref={refInput}
                defaultValue={currentDirName ?? ''}
                id={a11yMap.newDiskDirNameInput.id}
              />
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
                type="submit"
                variant="default"
                isLoading={mutationPlaylistUpdatePlaylist.isPending}
                disabled={mutationPlaylistUpdatePlaylist.isPending}
              >
                Update
              </Button>
            </Field>
          </FieldGroup>

        </FieldSet>

      </form>

    </DialogContent>
  );
}

// ui

function BlockWrapper({
  children,
  className,
  ...htmlProps
}: {
  children: React.ReactNode;
  className?: React.ComponentProps<"div">["className"];
} & Pick<React.ComponentProps<"div">, "role" | "aria-label">) {
  return (
    <div
      {...htmlProps}
      className={cn("flex flex-wrap justify-between border rounded-md overflow-hidden", className)}
    >
      {children}
    </div>
  );
}

function Block({
  title,
  className,
  children,
  ...htmlProps
}: {
  title: string;
  className?: React.ComponentProps<"div">["className"];
  children: React.ReactNode;
} & Pick<React.ComponentProps<"div">, | "aria-label" | "role">) {
  return (
    <div
      {...htmlProps}
      className={cn("flex-1 flex flex-col not-first:border-l", className)}
    >
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
