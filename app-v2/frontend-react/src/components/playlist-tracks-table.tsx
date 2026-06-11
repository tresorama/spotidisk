import type { ColumnDef } from "@tanstack/react-table";
import { SiSpotify, SiYoutube } from '@icons-pack/react-simple-icons';
import { CheckCircle2, Circle, DeleteIcon, Download, PencilIcon, PlayIcon, SearchIcon, TagIcon, TrashIcon } from "lucide-react";

import type { DerivedTrack } from "@/lib/api-client/types";

import { cn } from "#/lib/utils";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { TimeDurationMMSS } from "@/components/ui/time";

function Badge({
  text,
  variant = "default",
}: {
  text: string,
  variant?: "default" | "error";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full bg-muted px-2.5 py-1 text-xs font-semibold",
        variant === "default"
          ? "bg-muted"
          : "bg-destructive/10 text-destructive border border-destructive/40"
      )}
    >
      {text}
    </span>
  );
}

const columns: ColumnDef<DerivedTrack>[] = [
  {
    id: "track_number",
    header: "#",
    size: 50,
    cell: ({ row }) => row.index + 1,
  },
  {
    accessorKey: "title",
    header: "Song",
    size: 100,
    cell: ({ row }) => {
      return (
        <div className="flex flex-col gap-1">
          <span className="font-medium text-foreground">{row.original.title}</span>
          <span className="text-xs text-muted-foreground">{row.original.artists}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "spotify_id",
    header: "🎵 Spotify",
    size: 100,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center">
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.track_url} target="_blank" rel="noopener noreferrer">
                <SiSpotify />
              </a>
            )}
          />
          <TimeDurationMMSS durationInMs={row.original.duration_ms} />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.track_url} target="_blank" rel="noopener noreferrer">
                <PlayIcon />
              </a>
            )}
          />
        </div>
      );
    },
  },
  {
    accessorKey: "youtube_url",
    header: "🎬 YouTube",
    size: 100,
    cell: ({ row }) => {
      if (!row.original.youtube_url) {
        return (
          <div className="flex gap-2 items-center">
            <Circle className="size-5 text-muted-foreground" />
            <Badge text="Empty Linked Track" variant="error" />
          </div>
        );
      }
      return (
        <div className="flex gap-2 items-center">
          <CheckCircle2 className="size-5 text-green-500" />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.youtube_url} target="_blank" rel="noopener noreferrer">
                <SiYoutube />
              </a>
            )}
          />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.youtube_url} target="_blank" rel="noopener noreferrer">
                <DeleteIcon />
              </a>
            )}
          />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.youtube_url} target="_blank" rel="noopener noreferrer">
                <PencilIcon />
              </a>
            )}
          />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.youtube_url} target="_blank" rel="noopener noreferrer">
                <SearchIcon />
              </a>
            )}
            disabled
          />
        </div>
      );
    },
  },
  {
    accessorKey: "disk_file_duration",
    header: "💾 Disk",
    size: 100,
    cell: ({ row }) => {
      const hasDiskFile = (
        row.original.disk_file_duration !== undefined
        && row.original.disk_file_duration > 0
      );
      if (!hasDiskFile) {
        return (
          <div className="flex gap-2 items-center">
            <Circle className="size-5 text-muted-foreground" />
            <Badge text="Empty Linked Track" variant="error" />
            <Button
              variant="outline"
              size="sm"
              disabled={!hasDiskFile}
            >
              <Download className="size-4 mr-2" />
              Download
            </Button>
          </div>
        );
      }
      return (
        <div className="flex gap-2 items-center">
          <CheckCircle2 className="size-5 text-green-500" />
          <TimeDurationMMSS durationInMs={row.original.disk_file_duration ?? 0} />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <a href={row.original.disk_file_path} target="_blank" rel="noopener noreferrer">
                <Download className="size-4" />
              </a>
            )}
          />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <span>
                <TrashIcon />
              </span>
            )}
          />
          <Button
            variant="secondary"
            size="icon"
            render={(
              <span>
                <TagIcon />
              </span>
            )}
          />
        </div>
      );
    },
  },
  {
    accessorKey: "disk_file_path",
    header: "💾 Disk File Path",
    size: 100,
    cell: ({ row }) => {
      return (
        <div className="flex gap-2 items-center">
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
