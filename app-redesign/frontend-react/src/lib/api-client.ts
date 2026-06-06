import axios, { AxiosInstance } from 'axios'

// API Types (These should be generated from the backend's OpenAPI spec)
export interface TrackResponse {
  spotify_id: string
  title: string
  artists: string
  album: string
  release_date?: string
  duration_ms: number
  preview_url?: string
  cover_url?: string
  youtube_url?: string
  label?: string
  disk_file_duration?: number
}

export interface PlaylistListItem {
  id: string
  name: string
  owner: string
  cover_url?: string
  total_tracks: number
  description?: string
}

export interface PlaylistResponse {
  id: string
  name: string
  owner: string
  cover_url?: string
  total_tracks: number
  songs: TrackResponse[]
}

export interface DownloadRequest {
  track_id: string
  playlist_id: string
  youtube_url?: string
}

export interface EditMetadataRequest {
  track_id: string
  playlist_id: string
  title?: string
  artists?: string
  album?: string
  label?: string
}

export interface EditYoutubeUrlRequest {
  track_id: string
  playlist_id: string
  youtube_url: string
}

export interface ID3TagsResponse {
  frame_id: string
  tag_name: string
  value: string
  id3_version: string
}

export interface ID3TagsUpdateRequest {
  track_id: string
  playlist_id: string
  tags: Record<string, string>
}

// API Client
class ApiClient {
  private axiosInstance: AxiosInstance

  constructor(baseURL: string = '/api') {
    this.axiosInstance = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Playlists
  getPlaylists() {
    return this.axiosInstance.get<PlaylistListItem[]>('/playlists')
      .then(res => res.data)
  }

  getPlaylist(playlistId: string) {
    return this.axiosInstance.get<PlaylistResponse>(`/playlists/${playlistId}`)
      .then(res => res.data)
  }

  refreshPlaylist(playlistId: string) {
    return this.axiosInstance.post<PlaylistResponse>(
      `/playlists/${playlistId}/refresh`
    ).then(res => res.data)
  }

  // Download
  downloadTrack(request: DownloadRequest) {
    return this.axiosInstance.post('/download', request)
      .then(res => res.data)
  }

  syncPlaylist(playlistId: string) {
    return this.axiosInstance.post(`/sync/${playlistId}`)
      .then(res => res.data)
  }

  redownloadTrack(request: DownloadRequest) {
    return this.axiosInstance.post('/redownload', request)
      .then(res => res.data)
  }

  deleteTrack(trackId: string, playlistId: string) {
    return this.axiosInstance.delete(`/tracks/${trackId}`, {
      params: { playlist_id: playlistId },
    }).then(res => res.data)
  }

  // Metadata
  updateMetadata(request: EditMetadataRequest) {
    return this.axiosInstance.post(
      `/tracks/${request.track_id}/metadata`,
      request
    ).then(res => res.data)
  }

  // ID3 Tags
  getID3Tags(trackId: string, playlistId: string) {
    return this.axiosInstance.get<ID3TagsResponse[]>(
      `/tracks/${trackId}/tags`,
      { params: { playlist_id: playlistId } }
    ).then(res => res.data)
  }

  updateID3Tags(request: ID3TagsUpdateRequest) {
    return this.axiosInstance.post(
      `/tracks/${request.track_id}/tags`,
      request
    ).then(res => res.data)
  }

  // YouTube URL
  setYoutubeUrl(request: EditYoutubeUrlRequest) {
    return this.axiosInstance.post(
      `/tracks/${request.track_id}/youtube-url`,
      request
    ).then(res => res.data)
  }

  clearYoutubeUrl(trackId: string, playlistId: string) {
    return this.axiosInstance.delete(
      `/tracks/${trackId}/youtube-url`,
      { params: { playlist_id: playlistId } }
    ).then(res => res.data)
  }

  findYoutubeUrl(trackId: string, playlistId: string) {
    return this.axiosInstance.post(
      `/tracks/${trackId}/find-youtube`,
      { playlist_id: playlistId }
    ).then(res => res.data)
  }

  // Health
  getHealth() {
    return this.axiosInstance.get('/health')
      .then(res => res.data)
  }
}

export const apiClient = new ApiClient()
