
export interface DerivedTrack {
  spotify_id: string,
  track_url?: string,
  title: string,
  artists: string,
  album: string,
  release_date: string,
  duration_ms: number,
  youtube_url?: string,
  preview_url?: string,
  disk_file_duration?: number;
  disk_file_path: string;
}

export interface DerivedPlaylist {
  spotify_url: string,
  spotify_id: string,
  name: string,
  enabled: boolean,
  tracks: DerivedTrack[],
  tracks_count: number,
}