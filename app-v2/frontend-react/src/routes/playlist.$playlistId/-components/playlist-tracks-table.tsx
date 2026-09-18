import { useRef } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { SiSpotify, SiYoutube } from '@icons-pack/react-simple-icons';
import {
  CopyIcon,
  DeleteIcon,
  DownloadIcon,
  HardDriveIcon,
  InfoIcon,
  PencilIcon,
  PlayIcon,
  SearchIcon,
  TagIcon,
  TrashIcon,
} from "lucide-react";

import {
  apiClient,
  useMutationPlaylistDeleteTrackFromDisk,
  useMutationPlaylistDownloadSingleTrack,
  useMutationPlaylistFindTrackYoutubeUrlSingleTrack,
  useMutationPlaylistUpdateTrack,
  type DerivedTrack,
  type DerivedPlaylist
} from "#/data";

import { useToggle } from "#/utils/hooks/use-toggle";
import { useCopyToClipboard } from "#/utils/hooks/use-copy-to-clipboard";

import { cn } from "#/lib/utils";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { IconIsInvalid, IconIsValid } from "@/components/ui/icons-common";
import { TimeDurationMMSS } from "@/components/ui/time";
import { TooltipEasy } from "@/components/ui/tooltip-easy";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { PlayerYoutube } from "@/components/ui/player-youtube";
import { DebugOnly } from "@/components/ui/debug.with-state";
import { Field, FieldContent, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";


const columns: ColumnDef<DerivedTrack>[] = [
  {
    id: "track_number",
    header: () => (
      <span className="pl-1 flex gap-2 items-center">
        #
      </span>
    ),
    size: 50,
    cell: ({ row }) => {
      return (
        <div
          aria-label="Track Data"
          className="flex items-center gap-1 text-sm"
          data-track-id={row.original.spotify_id}
          data-track-index={row.index}
          data-playlist-id={row.original.spotify_playlist_id}
        >
          <span aria-label="Track Index">
            {row.index + 1}
          </span>
          <DebugOnly>
            <TooltipEasy
              classNameContent="w-180 max-w-[initial]"
              tooltipText={(
                <pre className="w-180 overflow-auto">
                  {JSON.stringify(row.original, null, 2)}
                </pre>
              )}
            >
              <InfoIcon className="size-[1em] text-muted-foreground" />
            </TooltipEasy>
          </DebugOnly>
        </div>
      );
    },
  },
  {
    id: "cover_image",
    header: "Cover",
    size: 100,
    cell: ({ row }) => {
      return (
        <div className="size-18 bg-muted overflow-hidden">
          {row.original.cover_url && (
            <img
              src={row.original.cover_url}
              alt={row.original.title}
              className="size-full object-cover"
            />
          )}
        </div>
      );
    }
  },
  {
    id: "song",
    accessorFn: (row) => row.title,
    header: "Song",
    // size: 220,
    // minSize: 220,
    cell: ({ row }) => {
      return (
        <div className="flex flex-col gap-1 pr-4">
          <span
            aria-label="Track Title"
            className="font-medium text-foreground"
          >
            {row.original.title}
          </span>
          <span
            aria-label="Track Artists"
            className="text-xs text-muted-foreground"
          >
            {row.original.artists}
          </span>
          <span
            aria-label="Track Album"
            className="text-xs text-muted-foreground"
          >
            ALB: {row.original.album || '-'}
          </span>
          <span
            aria-label="Track Label"
            className="text-xs text-muted-foreground"
          >
            LAB: {row.original.recording_label ?? '-'}
          </span>
        </div>
      );
    },
  },
  {
    id: "spotify",
    accessorFn: (row) => row.spotify_id,
    header: () => (
      <span className="pl-1 flex gap-2 items-center">
        <SiSpotify className="size-4" /> Spotify
      </span>
    ),
    // size: 100,
    // minSize: 170,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center pr-4">

          <TooltipEasy tooltipText="Open track in Spotify">
            <Button
              aria-label="Open track in Spotify"
              variant="secondary"
              size="icon"
              nativeButton={false}
              render={(
                <a
                  href={row.original.spotify_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <SiSpotify />
                </a>
              )}
            />
          </TooltipEasy>

          <TimeDurationMMSS
            aria-label="Spotify Duration"
            type="mm:ss"
            durationString={row.original.spotify_duration_mm_ss}
          />

          <Dialog>
            <TooltipEasy tooltipText="Open audio preview in Spotify">
              <DialogTrigger
                render={(
                  <Button
                    aria-label="Open audio preview in Spotify"
                    variant="secondary"
                    size="icon"
                    disabled={!row.original.spotify_preview_url}
                  >
                    <PlayIcon />
                  </Button>
                )}
              />
            </TooltipEasy>
            <DialogContentSpotifyPreview
              spotifyPreviewUrl={row.original.spotify_preview_url}
            />
          </Dialog>

        </div>
      );
    },
  },
  {
    id: "youtube",
    accessorFn: (row) => row.youtube_url,
    header: () => (
      <span className="pl-1 flex gap-2 items-center">
        <SiYoutube className="size-4" /> YouTube
      </span>
    ),
    // size: 100,
    // minSize: 200,
    cell: ({ row }) => {

      const mutationUpdateTrack = useMutationPlaylistUpdateTrack();
      const mutationFindTrackYoutubeUrl = useMutationPlaylistFindTrackYoutubeUrlSingleTrack();
      const copyToClipboard = useCopyToClipboard();

      const dialogSetYoutubeUrlVisibility = useToggle({ initialValue: false });

      const buildManualSearchUrl = (track: DerivedTrack) => {
        const url = new URL("https://www.youtube.com/results");
        url.searchParams.set("search_query", `${track.artists} ${track.title}`);
        return url.toString();
      };

      const handleSetYoutubeUrl = (newUrl: string | null) => {
        if (!newUrl) {
          return;
        }
        mutationUpdateTrack.mutate({
          body: {
            playlist_id: row.original.spotify_playlist_id,
            track_id: row.original.spotify_id,
            youtube_url: newUrl,
          }
        });
        dialogSetYoutubeUrlVisibility.setValue(false);
      };
      const handleClearYoutubeUrl = () => {
        mutationUpdateTrack.mutate({
          body: {
            playlist_id: row.original.spotify_playlist_id,
            track_id: row.original.spotify_id,
            youtube_url: null,
          }
        });
      };
      const handleFindYouTubeUrl = () => {
        mutationFindTrackYoutubeUrl.mutate({
          path: {
            playlist_id: row.original.spotify_playlist_id,
            track_id: row.original.spotify_id,
          }
        });
      };
      const handleCopyYoutubeUrlToClipboard = () => {
        if (!row.original.youtube_url) {
          return;
        }
        copyToClipboard.copy({
          text: row.original.youtube_url,
          showToast: true
        });
      };

      return (
        <div className="flex gap-2 items-center pr-4">

          <TooltipEasy tooltipText={!row.original.youtube_url ? "No Youtube track is linked" : "A Youtube track is linked"}>
            <div aria-label="Youtube Track Link Status">
              {row.original.youtube_url ? (
                <>
                  <IconIsValid className="size-5" />
                  <span className="sr-only">A Youtube track is linked</span>
                </>
              ) : (
                <>
                  <IconIsInvalid className="size-5" />
                  <span className="sr-only">No Youtube track is linked</span>
                </>
              )}
            </div>
          </TooltipEasy>

          {!row.original.youtube_url ? (
            <>
              <TooltipEasy tooltipText="Auto Search - Find and set the best YouTube URL match for this track. If nothing is found use manual search">
                <Button
                  aria-label="Do Auto Search URL for this track"
                  onClick={handleFindYouTubeUrl}
                  isLoading={mutationFindTrackYoutubeUrl.isPending}
                  variant="secondary"
                  size="icon"
                >
                  <SearchIcon />
                </Button>
              </TooltipEasy>

              <TooltipEasy tooltipText="Manual Search - Open Youtube search in new tab with search populated">
                <Button
                  aria-label="Open Manual Search for this track"
                  variant="secondary"
                  size="icon"
                  nativeButton={false}
                  render={(
                    <a
                      href={buildManualSearchUrl(row.original)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <SearchIcon />
                    </a>
                  )}
                />
              </TooltipEasy>
            </>
          ) : (
            <>
              <Dialog>
                <TooltipEasy tooltipText="Open track in YouTube">
                  <DialogTrigger
                    render={(
                      <Button
                        aria-label="Open track in YouTube"
                        variant="secondary"
                        size="icon"
                      >
                        <SiYoutube />
                      </Button>
                    )}
                  />
                </TooltipEasy>
                <DialogContentYuotubePreview
                  youtubeUrl={row.original.youtube_url}
                />
              </Dialog>
            </>
          )}

          <Dialog
            open={dialogSetYoutubeUrlVisibility.value}
            onOpenChange={dialogSetYoutubeUrlVisibility.setValue}
          >
            <TooltipEasy tooltipText="Set/Update YouTube URL">
              <DialogTrigger
                render={(
                  <Button
                    aria-label="Set/Update YouTube URL"
                    isLoading={mutationUpdateTrack.isPending}
                    variant="secondary"
                    size="icon"
                  >
                    <PencilIcon />
                  </Button>
                )}
              />
            </TooltipEasy>
            <DialogContentSetYoutubeUrl
              currentYoutubeUrl={row.original.youtube_url}
              onConfirmed={handleSetYoutubeUrl}
            />
          </Dialog>

          {row.original.youtube_url && (
            <>
              <TooltipEasy tooltipText="Delete YouTube URL for this track (clear it)">
                <Button
                  aria-label="Clear YouTube URL for this track"
                  onClick={handleClearYoutubeUrl}
                  isLoading={mutationUpdateTrack.isPending}
                  variant="secondary"
                  size="icon"
                >
                  <DeleteIcon className="-translate-x-px" />
                </Button>
              </TooltipEasy>

              <TooltipEasy tooltipText="Copy YouTube URL for this track to clipboard">
                <Button
                  aria-label="Copy YouTube URL for this track to clipboard"
                  onClick={handleCopyYoutubeUrlToClipboard}
                  variant="secondary"
                  size="icon"
                >
                  <CopyIcon />
                </Button>
              </TooltipEasy>
            </>
          )}

        </div>
      );

    },
  },
  {
    id: "disk",
    accessorFn: (row) => row.disk_file_name,
    header: () => (
      <span className="pl-1 flex gap-2 items-center">
        <HardDriveIcon className="size-4" /> Disk
      </span>
    ),
    // size: 100,
    // minSize: 300,
    cell: ({ row }) => {
      const mutationDownloadTrack = useMutationPlaylistDownloadSingleTrack();
      const mutationDeleteTrack = useMutationPlaylistDeleteTrackFromDisk();

      const handleDownloadTrack = () => {
        // mutationDownloadTrack.mutate({
        //   playlistId: row.original.spotify_playlist_id,
        //   trackId: row.original.spotify_id
        // });
        mutationDownloadTrack.mutate({
          path: {
            playlist_id: row.original.spotify_playlist_id,
            track_id: row.original.spotify_id
          }
        });
      };
      const handleDeleteTrack = () => {
        // mutationDeleteTrack.mutate({
        //   playlistId: row.original.spotify_playlist_id,
        //   trackId: row.original.spotify_id
        // });
        mutationDeleteTrack.mutate({
          path: {
            playlist_id: row.original.spotify_playlist_id,
            track_id: row.original.spotify_id
          }
        });
      };

      const hasDiskFile = row.original.has_disk_file;

      return (
        <div className="flex gap-2 items-center pr-4">

          <TooltipEasy tooltipText={!row.original.youtube_url ? "File on disk not present/not downloaded" : "File on disk present/ already downloaded"}>
            <div aria-label="Disk Track Link Status">
              {hasDiskFile ? (
                <>
                  <IconIsValid className="size-5" />
                  <span className="sr-only">File on disk present/ already downloaded</span>
                </>
              ) : (
                <>
                  <IconIsInvalid className="size-5" />
                  <span className="sr-only">File on disk not present/not downloaded</span>
                </>
              )}
            </div>
          </TooltipEasy>

          {hasDiskFile && (
            <TimeDurationMMSS
              aria-label="Disk Track Duration"
              type="mm:ss"
              durationString={row.original.disk_file_duration_mm_ss ?? '- : -'}
            />
          )}

          {hasDiskFile && (
            <Dialog>
              <TooltipEasy tooltipText="Play downloaded track from disk">
                <DialogTrigger
                  render={(
                    <Button
                      aria-label="Play downloaded track from disk"
                      variant="secondary"
                      size="icon"
                    >
                      <PlayIcon />
                    </Button>
                  )}
                />
              </TooltipEasy>
              <DialogContentDiskPreview
                playlistId={row.original.spotify_playlist_id}
                trackId={row.original.spotify_id}
              />
            </Dialog>
          )}

          <TooltipEasy tooltipText="Download/Re-download track from YouTube">
            <Button
              aria-label="Download/Re-download track from YouTube"
              onClick={handleDownloadTrack}
              disabled={mutationDownloadTrack.isPending}
              isLoading={mutationDownloadTrack.isPending}
              variant="secondary"
            >
              <DownloadIcon />
              Download
            </Button>
          </TooltipEasy>

          {hasDiskFile && (
            <TooltipEasy tooltipText="Delete track from disk">
              <Button
                aria-label="Delete track from disk"
                onClick={handleDeleteTrack}
                disabled={mutationDeleteTrack.isPending}
                isLoading={mutationDeleteTrack.isPending}
                variant="secondary"
                size="icon"
              >
                <TrashIcon />
              </Button>
            </TooltipEasy>
          )}

          {hasDiskFile && (
            <Button
              variant="secondary"
              size="icon"
            >
              <TagIcon />
            </Button>
          )}


        </div>
      );

    },
  },
  {
    id: "disk_file_name",
    accessorFn: (row) => row.disk_file_name,
    header: () => (
      <span className="flex gap-2 items-center">
        <HardDriveIcon className="size-4" /> Disk File Name
      </span>
    ),
    // size: 100,
    cell: ({ row }) => {
      const copyToClipboard = useCopyToClipboard();

      const handleCopyDiskFileNameToClipboard = () => {
        copyToClipboard.copy({
          text: row.original.disk_file_name,
        });
      };

      return (
        <div className="flex gap-2 items-center pr-4">
          <TooltipEasy tooltipText="Copy disk file name to clipboard">
            <Button
              aria-label="Copy disk file name to clipboard"
              onClick={handleCopyDiskFileNameToClipboard}
              variant="secondary"
              size="icon"
            >
              <CopyIcon />
            </Button>
          </TooltipEasy>
          <span
            aria-label="Disk File Name"
            className="text-xs text-muted-foreground"
          >
            {row.original.disk_file_name}
          </span>
        </div>
      );
    },
  },
  {
    id: "disk_file_path",
    accessorFn: (row) => row.disk_file_path,
    header: () => (
      <span className="flex gap-2 items-center">
        <HardDriveIcon className="size-4" /> Disk File Path
      </span>
    ),
    // size: 100,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center pr-4">
          <span
            aria-label="Disk File Path"
            className="text-xs text-muted-foreground"
          >
            {row.original.disk_file_path}
          </span>
        </div>
      );
    },
  },
];

interface PlaylistTracksTableProps {
  tracks: DerivedTrack[];
  playlistId: DerivedPlaylist['spotify_id'];
  className?: React.ComponentProps<"div">["className"];
}

export function PlaylistTracksTable({
  tracks,
  playlistId,
  className,
}: PlaylistTracksTableProps) {
  return (
    <DataTable
      role="group"
      aria-label="Playlist Tracks Table"
      data-playlist-id={playlistId}
      columns={columns}
      data={tracks}
      classNameWrapper={cn("w-full h-full *:h-full", className)}
      classNameTHead="sticky top-0 z-10"
    />
  );
}

function DialogContentSpotifyPreview({ spotifyPreviewUrl }: { spotifyPreviewUrl: string; }) {
  return (
    <DialogContent className="w-200 sm:max-w-[80dvw]">
      <DialogHeader>
        <DialogTitle>
          Spotify Track Preview
        </DialogTitle>
        <DialogDescription>
          30 seconds of audio preview of the Spotify track
        </DialogDescription>
      </DialogHeader>
      <audio
        src={spotifyPreviewUrl}
        controls
        autoPlay
        className="w-full"
      />
    </DialogContent>
  );
}

function DialogContentYuotubePreview({ youtubeUrl }: { youtubeUrl: string; }) {
  return (
    <DialogContent className="w-240 sm:max-w-[80dvw]">
      <DialogHeader>
        <DialogTitle>
          YouTube Track Preview
        </DialogTitle>
        <DialogDescription>
          The linked track on Youtube that will be downloaded to disk
        </DialogDescription>
      </DialogHeader>
      <div className="w-full aspect-video">
        <PlayerYoutube
          src={youtubeUrl}
          controls
          autoPlay
        />
      </div>
    </DialogContent>
  );
}


function DialogContentDiskPreview({ playlistId, trackId }: { playlistId: string; trackId: string; }) {
  return (
    <DialogContent className="w-200 sm:max-w-[80dvw]">
      <DialogHeader>
        <DialogTitle>
          Disk Track Preview
        </DialogTitle>
        <DialogDescription>
          This track is already downloaded to disk
        </DialogDescription>
      </DialogHeader>
      <audio
        src={apiClient.apiHttp.getUrl__playlist_disk_getAudioFile({
          playlistId,
          trackId,
        })}
        controls
        autoPlay
        className="w-full"
      />
    </DialogContent>
  );
}

function DialogContentSetYoutubeUrl({
  currentYoutubeUrl,
  onConfirmed,
}: {
  currentYoutubeUrl?: string | null;
  onConfirmed: (newUrl: string | null) => void;
}) {

  const refInput = useRef<HTMLInputElement>(null);
  const handleFormSubmit = () => {
    const data = {
      youtube_url: refInput.current?.value ?? null,
    };
    onConfirmed(data.youtube_url);
  };

  return (
    <DialogContent className="w-240 sm:max-w-[80dvw]">
      <DialogHeader>
        <DialogTitle>
          Set Youtube URL Manually
        </DialogTitle>
        <DialogDescription>
          This action will overwrite the current Youtube URL
        </DialogDescription>
      </DialogHeader>

      <form
        aria-label="Form Set Youtube URL Manually"
        onSubmit={e => {
          e.preventDefault();
          e.stopPropagation();
          handleFormSubmit();
        }}
      >
        <FieldGroup>
          <Field>
            <FieldLabel
              aria-label="Youtube URL"
              htmlFor="newYoutubeUrlInput"
            >
              Youtube URL
            </FieldLabel>
            <Input
              ref={refInput}
              id="newYoutubeUrlInput"
              defaultValue={currentYoutubeUrl ?? ''}
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
            >
              Update
            </Button>
          </Field>
        </FieldGroup>
      </form>

    </DialogContent>
  );
}