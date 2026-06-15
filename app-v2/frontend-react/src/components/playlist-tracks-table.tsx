import type { ColumnDef } from "@tanstack/react-table";
import { SiSpotify, SiYoutube } from '@icons-pack/react-simple-icons';
import {
  CopyIcon,
  DeleteIcon,
  DownloadIcon,
  HardDriveIcon,
  PencilIcon,
  PlayIcon,
  SearchIcon,
  TagIcon,
  TrashIcon,
} from "lucide-react";

import type { DerivedTrack } from "@/lib/api-client/types";
import { apiClient } from "@/lib/api-client/client";
import {
  useMutationPlaylistDeleteTrackFromDisk,
  useMutationPlaylistDownloadSingleTrackFromYoutubeToDisk,
  useMutationPlaylistFindTrackYoutubeUrl,
  useMutationPlaylistUpdateTrack
} from "@/hooks/use-playlists";

import { useCopyToClipboard } from "@/hooks/use-copy-to-clipboard";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { IconIsInvalid, IconIsValid } from "@/components/ui/icons-common";
import { TimeDurationMMSS } from "@/components/ui/time";
import { TooltipEasy } from "@/components/ui/tooltip-easy";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { PlayerYoutube } from "@/components/ui/player-youtube";

const columns: ColumnDef<DerivedTrack>[] = [
  {
    id: "track_number",
    header: "#",
    size: 50,
    cell: ({ row }) => row.index + 1,
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
          <span className="font-medium text-foreground">{row.original.title}</span>
          <span className="text-xs text-muted-foreground">{row.original.artists}</span>
        </div>
      );
    },
  },
  {
    id: "spotify",
    accessorFn: (row) => row.spotify_id,
    header: () => (
      <span className="flex gap-2 items-center">
        <SiSpotify /> Spotify
      </span>
    ),
    // size: 100,
    // minSize: 170,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center pr-4">
          <TooltipEasy tooltipText="Open track in Spotify">
            <Button
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
            type="mm:ss"
            durationString={row.original.spotify_duration_mm_ss}
          />
          <Dialog>
            <DialogTrigger>
              <TooltipEasy tooltipText="Open audio preview in Spotify">
                <Button
                  variant="secondary"
                  size="icon"
                  disabled={!row.original.spotify_preview_url}
                >
                  <PlayIcon />
                </Button>
              </TooltipEasy>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Spotify Audio Preview</DialogTitle>
                <DialogDescription>
                  30 seconds of audio preview of the Spotify track
                </DialogDescription>
              </DialogHeader>
              <audio
                src={row.original.spotify_preview_url}
                controls
                autoPlay
              />
            </DialogContent>
          </Dialog>
        </div>
      );
    },
  },
  {
    id: "youtube",
    accessorFn: (row) => row.youtube_url,
    header: () => (
      <span className="flex gap-2 items-center">
        <SiYoutube /> YouTube
      </span>
    ),
    // size: 100,
    // minSize: 200,
    cell: ({ row }) => {

      const mutationUpdateTrack = useMutationPlaylistUpdateTrack();
      const mutationFindTrackYoutubeUrl = useMutationPlaylistFindTrackYoutubeUrl();
      const copyToClipboard = useCopyToClipboard();


      const buildManualSearchUrl = (track: DerivedTrack) => {
        const url = new URL("https://www.youtube.com/results");
        url.searchParams.set("search_query", `${track.artists} ${track.title}`);
        return url.toString();
      };

      const handleSetYoutubeUrl = () => {
        const userUrl = prompt("Enter a YouTube URL");
        if (userUrl) {
          mutationUpdateTrack.mutate({
            playlist_id: row.original.spotify_playlist_id,
            track_id: row.original.spotify_id,
            youtube_url: userUrl,
          });
        }
      };
      const handleClearYoutubeUrl = () => {
        mutationUpdateTrack.mutate({
          playlist_id: row.original.spotify_playlist_id,
          track_id: row.original.spotify_id,
          youtube_url: null,
        });
      };
      const handleFindYouTubeUrl = () => {
        mutationFindTrackYoutubeUrl.mutate({
          playlistId: row.original.spotify_playlist_id,
          trackId: row.original.spotify_id,
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

      if (!row.original.youtube_url) {
        return (
          <div className="flex gap-2 items-center pr-4">
            <TooltipEasy tooltipText="No Linked YouTube track">
              <IconIsInvalid className="size-5" />
            </TooltipEasy>
            <TooltipEasy tooltipText="Set/Update YouTube URL">
              <Button
                onClick={handleSetYoutubeUrl}
                isLoading={mutationUpdateTrack.isPending}
                variant="secondary"
                size="icon"
              >
                <PencilIcon />
              </Button>
            </TooltipEasy>
            <TooltipEasy tooltipText="Auto Search - Find and set the best YouTube URL match for this track. If nothing is found use manual search">
              <Button
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
          </div>
        );
      }

      return (
        <div className="flex gap-2 items-center pr-4">
          <TooltipEasy tooltipText="A Youtube track is linked">
            <IconIsValid className="size-5" />
          </TooltipEasy>
          <Dialog>
            <DialogTrigger>
              <TooltipEasy tooltipText="Open track in YouTube">
                <Button
                  variant="secondary"
                  size="icon"
                >
                  <SiYoutube />
                </Button>
              </TooltipEasy>
            </DialogTrigger>
            <DialogContent className="w-160 sm:max-w-[80dvw]">
              <DialogHeader>
                <DialogTitle>YouTube Track</DialogTitle>
                <DialogDescription>
                  The linked track on Youtube that will be downloaded to disk
                </DialogDescription>
              </DialogHeader>
              <div className="w-full aspect-video">
                <PlayerYoutube
                  src={row.original.youtube_url}
                  controls
                  autoPlay
                />
              </div>
            </DialogContent>
          </Dialog>
          <TooltipEasy tooltipText="Delete YouTube URL for this track (clear it)">
            <Button
              onClick={handleClearYoutubeUrl}
              isLoading={mutationUpdateTrack.isPending}
              variant="secondary"
              size="icon"
            >
              <DeleteIcon className="-translate-x-px" />
            </Button>
          </TooltipEasy>
          <TooltipEasy tooltipText="Update YouTube URL for this track">
            <Button
              onClick={handleSetYoutubeUrl}
              isLoading={mutationUpdateTrack.isPending}
              variant="secondary"
              size="icon"
            >
              <PencilIcon />
            </Button>
          </TooltipEasy>
          <TooltipEasy tooltipText="Copy YouTube URL for this track to clipboard">
            <Button
              onClick={handleCopyYoutubeUrlToClipboard}
              variant="secondary"
              size="icon"
            >
              <CopyIcon />
            </Button>
          </TooltipEasy>
        </div>
      );
    },
  },
  {
    id: "disk",
    accessorFn: (row) => row.disk_file_name,
    header: () => (
      <span className="flex gap-2 items-center">
        <HardDriveIcon /> Disk
      </span>
    ),
    // size: 100,
    // minSize: 300,
    cell: ({ row }) => {
      const mutationDownloadTrack = useMutationPlaylistDownloadSingleTrackFromYoutubeToDisk();
      const mutationDeleteTrack = useMutationPlaylistDeleteTrackFromDisk();

      const handleDownloadTrack = () => {
        mutationDownloadTrack.mutate({
          playlistId: row.original.spotify_playlist_id,
          trackId: row.original.spotify_id
        });
      };
      const handleDeleteTrack = () => {
        mutationDeleteTrack.mutate({
          playlistId: row.original.spotify_playlist_id,
          trackId: row.original.spotify_id
        });
      };


      const hasDiskFile = row.original.has_disk_file;
      if (!hasDiskFile) {
        return (
          <div className="flex gap-2 items-center pr-4">
            <TooltipEasy tooltipText="File on disk not present/not downloaded">
              <IconIsInvalid className="size-5" />
            </TooltipEasy>
            <TooltipEasy tooltipText="Download/Re-download track from YouTube">
              <Button
                onClick={handleDownloadTrack}
                disabled={mutationDownloadTrack.isPending}
                isLoading={mutationDownloadTrack.isPending}
                variant="secondary"
              >
                <DownloadIcon />
                Download
              </Button>
            </TooltipEasy>
          </div>
        );
      }

      return (
        <div className="flex gap-2 items-center pr-4">
          <TooltipEasy tooltipText="File on disk present/ already downloaded">
            <IconIsValid className="size-5" />
          </TooltipEasy>
          <TimeDurationMMSS
            type="mm:ss"
            durationString={row.original.disk_file_duration_mm_ss ?? '- : -'}
          />
          <Dialog>
            <DialogTrigger>
              <TooltipEasy tooltipText="Play downloaded track from disk">
                <Button
                  variant="secondary"
                  size="icon"
                >
                  <PlayIcon />
                </Button>
              </TooltipEasy>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Disk Track</DialogTitle>
                <DialogDescription>
                  This track is already downloaded to disk
                </DialogDescription>
              </DialogHeader>
              <audio
                src={apiClient.playlist_disk_getAudioFile_BUILD_URL({
                  playlistId: row.original.spotify_playlist_id,
                  trackId: row.original.spotify_id,
                })}
                controls
                autoPlay
              />
            </DialogContent>
          </Dialog>
          <Button
            onClick={handleDownloadTrack}
            disabled={mutationDownloadTrack.isPending}
            isLoading={mutationDownloadTrack.isPending}
            variant="secondary"
          >
            <DownloadIcon />
            Re-Download
          </Button>
          <TooltipEasy tooltipText="Delete track from disk">
            <Button
              onClick={handleDeleteTrack}
              disabled={mutationDeleteTrack.isPending}
              isLoading={mutationDeleteTrack.isPending}
              variant="secondary"
              size="icon"
            >
              <TrashIcon />
            </Button>
          </TooltipEasy>
          <Button
            variant="secondary"
            size="icon"
          >
            <TagIcon />
          </Button>
        </div>
      );
    },
  },
  {
    id: "disk_file_name",
    accessorFn: (row) => row.disk_file_name,
    header: () => (
      <span className="flex gap-2 items-center">
        <HardDriveIcon /> Disk File Name
      </span>
    ),
    // size: 100,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center pr-4">
          <span className="text-xs text-muted-foreground">
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
        <HardDriveIcon /> Disk File Path
      </span>
    ),
    // size: 100,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center pr-4">
          <span className="text-xs text-muted-foreground">
            {row.original.disk_file_path}
          </span>
        </div>
      );
    },
  },
];

interface PlaylistTracksTableProps {
  tracks: DerivedTrack[];
}

export function PlaylistTracksTable({ tracks }: PlaylistTracksTableProps) {
  return (
    <DataTable
      columns={columns}
      data={tracks}
      classNameWrapper="h-full *:h-full"
      classNameTHead="sticky top-0 z-10"
    />
  );
}
