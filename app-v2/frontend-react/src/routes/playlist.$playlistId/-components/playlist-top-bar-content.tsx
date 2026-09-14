import { HardDriveIcon } from "lucide-react";
import { SiSpotify, SiYoutube } from "@icons-pack/react-simple-icons";

import type { DerivedPlaylist } from "#/data";

import { PlaylistTitle } from "./playlist-title";

import { Badge } from "#/components/ui/badge";
import { Button } from "#/components/ui/button";
import { DebugOnlyTooltipData } from "#/components/ui/debug.with-state";
import { IconIsValid } from "#/components/ui/icons-common";
import { TooltipEasy } from "#/components/ui/tooltip-easy";

export function PlaylistTopBarContent({
  playlist,
  onRefresh,
}: {
  playlist: DerivedPlaylist;
  onRefresh: () => void;
}) {

  return (
    <>
      <PlaylistTitle
        playlistId={playlist.spotify_id}
        playlist={playlist}
      />
      <TracksCounter
        tracksCountSpotify={playlist.tracks_count}
        tracksCountYoutube={playlist.tracks_count_youtube}
        tracksCountDisk={playlist.tracks_count_disk}
      />
      <DebugOnlyTooltipData
        data={playlist}
      />
      <Button
        variant="secondary"
        onClick={() => onRefresh()}
        className="ml-auto"
      >
        Refresh
      </Button>
    </>
  );
}


// ui

function TracksCounter({
  tracksCountSpotify,
  tracksCountYoutube,
  tracksCountDisk,
}: {
  tracksCountSpotify: number;
  tracksCountYoutube: number;
  tracksCountDisk: number;
}) {

  const missingYoutubeTracksCount = tracksCountSpotify - tracksCountYoutube;
  const missingDiskTracksCount = tracksCountYoutube - tracksCountDisk;
  const messageYoutube = tracksCountSpotify === 0
    ? "No Spotify tracks, please Fetch them first"
    : missingYoutubeTracksCount === 0
      ? `All "Spotify" tracks are linked to Youtube`
      : [
        `There are ${tracksCountSpotify} Spotify tracks. But ${missingYoutubeTracksCount} of them `,
        missingYoutubeTracksCount === 1 ? `is ` : `are `,
        "not linked to Youtube",
      ].join("");
  const messageDisk = tracksCountSpotify === 0
    ? "No Spotify tracks, please Fetch them first"
    : missingDiskTracksCount === 0
      ? `All "Linked to Youtube" tracks are downloaded to Disk`
      : [
        `There are ${tracksCountYoutube} "linked to Youtube" tracks. But ${missingDiskTracksCount} of them `,
        missingDiskTracksCount === 1 ? `is ` : `are `,
        "not downloaded to Disk",
      ];

  const JsxSeparator = (
    <span
      role="separator"
      className="px-1 text-muted-foreground/20 font-extralight"
    >
      {" | "}
    </span>
  );


  return (
    <Badge
      role="group"
      aria-label="Playlist Tracks Count"
      variant="outline"
      size="lg"
    >
      <div
        aria-label="Spotify Tracks Count"
        className="flex items-center gap-[inherit]"
      >
        <SiSpotify />
        <span>
          {tracksCountSpotify}
        </span>
      </div>

      {JsxSeparator}

      <div
        aria-label="Youtube Tracks Count"
        className="flex items-center gap-[inherit]"
      >
        <SiYoutube />
        <span>
          {tracksCountYoutube}
        </span>
        {missingYoutubeTracksCount === 0 ? (
          <TooltipEasy tooltipText={messageYoutube}>
            <IconIsValid />
          </TooltipEasy>
        ) : (
          <TooltipEasy tooltipText={messageYoutube}>
            <span className="text-destructive">
              {-1 * missingYoutubeTracksCount}
            </span>
          </TooltipEasy>
        )}
      </div>

      {JsxSeparator}

      <div
        aria-label="Disk Tracks Count"
        className="flex items-center gap-[inherit]"
      >
        <HardDriveIcon />
        <span>
          {tracksCountDisk}
        </span>
        {missingDiskTracksCount === 0 ? (
          <TooltipEasy tooltipText={messageDisk}>
            <IconIsValid />
          </TooltipEasy>
        ) : (
          <TooltipEasy tooltipText={messageDisk}>
            <span className="text-destructive">
              {-1 * missingDiskTracksCount}
            </span>
          </TooltipEasy>
        )}
      </div>

    </Badge>
  );
};