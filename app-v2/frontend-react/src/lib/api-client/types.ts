// main types

export interface DerivedTrack {
  spotify_id: string,
  spotify_url: string,
  spotify_playlist_id: string,
  spotify_preview_url: string,
  spotify_duration_ms: number,
  spotify_duration_mm_ss: string,
  title: string,
  artists: string,
  album: string,
  youtube_url?: string,
  disk_file_name: string,
  disk_file_name_without_extension: string,
  disk_file_path: string,
  disk_file_path_without_extension: string,
  has_disk_file: boolean,
  disk_file_duration_ms?: number | null,
  disk_file_duration_mm_ss?: string | null,
}

export interface DerivedPlaylist {
  spotify_id: string,
  spotify_url: string,
  name: string,
  enabled: boolean,
  tracks: DerivedTrack[],
  tracks_count: number,
  disk_path: string,
}


// edit types

export interface PlaylistEditTrackPayload {
  playlist_id: string,
  track_id: string,
  youtube_url?: string | null;
}

// ws types

export interface JobGetStatusResponse {
  dateTimeISO: string;
  hasJob: boolean;
  data?: {
    title: string;
    /** 0-1 range */
    progress: number;
    isRunning: boolean;
    isFinished: boolean;
  };
}