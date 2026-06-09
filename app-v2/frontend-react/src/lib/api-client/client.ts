import axios, { type AxiosInstance } from 'axios';
import type {
  DownloadRequest,
  EditMetadataRequest,
  EditYoutubeUrlRequest,
  ID3TagsResponse,
  ID3TagsUpdateRequest,

  DerivedPlaylist,
} from './types';

class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor(config: {
    baseURL: string;
  }) {
    this.axiosInstance = axios.create({
      baseURL: config.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ========== Playlists ==========

  getPlaylists() {
    return this.axiosInstance
      .get<DerivedPlaylist[]>('/playlists')
      .then((res) => res.data);
  }

  getPlaylist(playlistId: DerivedPlaylist['spotify_id']) {
    return this.axiosInstance
      .get<DerivedPlaylist>(`/playlists/${playlistId}`)
      .then((res) => res.data);
  }

  refreshPlaylist(playlistId: DerivedPlaylist['spotify_id']) {
    return this.axiosInstance
      .post<DerivedPlaylist>(`/playlists/${playlistId}/refresh`)
      .then((res) => res.data);
  }

  // ========== Downloads ==========

  downloadTrack(request: DownloadRequest) {
    return this.axiosInstance
      .post('/download', request)
      .then((res) => res.data);
  }

  syncPlaylist(playlistId: string) {
    return this.axiosInstance
      .post(`/sync/${playlistId}`)
      .then((res) => res.data);
  }

  redownloadTrack(request: DownloadRequest) {
    return this.axiosInstance
      .post('/redownload', request)
      .then((res) => res.data);
  }

  deleteTrack(trackId: string, playlistId: string) {
    return this.axiosInstance
      .delete(`/tracks/${trackId}`, {
        params: { playlist_id: playlistId },
      })
      .then((res) => res.data);
  }

  // ========== Metadata ==========

  updateMetadata(request: EditMetadataRequest) {
    return this.axiosInstance
      .post(`/tracks/${request.track_id}/metadata`, request)
      .then((res) => res.data);
  }

  // ========== ID3 Tags ==========

  getID3Tags(trackId: string, playlistId: string) {
    return this.axiosInstance
      .get<ID3TagsResponse[]>(`/tracks/${trackId}/tags`, {
        params: { playlist_id: playlistId },
      })
      .then((res) => res.data);
  }

  updateID3Tags(request: ID3TagsUpdateRequest) {
    return this.axiosInstance
      .post(`/tracks/${request.track_id}/tags`, request)
      .then((res) => res.data);
  }

  // ========== YouTube URLs ==========

  setYoutubeUrl(request: EditYoutubeUrlRequest) {
    return this.axiosInstance
      .post(`/tracks/${request.track_id}/youtube-url`, request)
      .then((res) => res.data);
  }

  clearYoutubeUrl(trackId: string, playlistId: string) {
    return this.axiosInstance
      .delete(`/tracks/${trackId}/youtube-url`, {
        params: { playlist_id: playlistId },
      })
      .then((res) => res.data);
  }

  findYoutubeUrl(trackId: string, playlistId: string) {
    return this.axiosInstance
      .post(`/tracks/${trackId}/find-youtube`, {
        playlist_id: playlistId,
      })
      .then((res) => res.data);
  }

  // ========== Health ==========

  getHealth() {
    return this.axiosInstance
      .get('/health')
      .then((res) => res.data);
  }
}

export const apiClient = new ApiClient({
  baseURL: 'http://127.0.0.1:8000',
});
