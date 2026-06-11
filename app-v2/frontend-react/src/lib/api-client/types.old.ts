
// ============================================================================
// Type Definitions (from backend Pydantic models)
// ============================================================================

export interface TrackResponse {
  spotify_id: string;
  title: string;
  artists: string;
  album: string;
  release_date?: string;
  duration_ms: number;
  preview_url?: string;
  cover_url?: string;
  youtube_url?: string;
  label?: string;
  disk_file_duration?: number;
}

export interface PlaylistListItem {
  id: string;
  name: string;
  owner: string;
  cover_url?: string;
  total_tracks: number;
  description?: string;
}

export interface PlaylistResponse {
  id: string;
  name: string;
  owner: string;
  cover_url?: string;
  total_tracks: number;
  songs: TrackResponse[];
}

export interface DownloadRequest {
  track_id: string;
  playlist_id: string;
  youtube_url?: string;
}

export interface EditMetadataRequest {
  track_id: string;
  playlist_id: string;
  title?: string;
  artists?: string;
  album?: string;
  label?: string;
}

export interface EditYoutubeUrlRequest {
  track_id: string;
  playlist_id: string;
  youtube_url: string;
}

export interface ID3TagsResponse {
  frame_id: string;
  tag_name: string;
  value: string;
  id3_version: string;
}

export interface ID3TagsUpdateRequest {
  track_id: string;
  playlist_id: string;
  tags: Record<string, string>;
}

export interface ApiResponse<T = unknown> {
  status: string;
  data?: T;
}