import type { DerivedPlaylist } from "#/data";

export function PlaylistTitle({
  playlistId,
  playlist,
}: {
  playlistId: string;
  playlist: DerivedPlaylist | null;
}) {
  if (!playlist) {
    return (
      <h1
        className="font-semibold"
        aria-label="Error loading playlist"
        data-playlist-id={playlistId}
        data-playlist-fetch-status="ERROR_OR_NOT_FOUND"
      >
        Error loading playlist
      </h1>
    );
  }

  return (
    <h1
      className="font-semibold"
      aria-label="Playlist Title"
      data-playlist-id={playlistId}
      data-playlist-fetch-status="FOUND"
    >
      {playlist.name}
    </h1>
  );
}