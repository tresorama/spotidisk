import axios, { type AxiosInstance } from 'axios';
import type {
  DerivedPlaylist,
  DerivedTrack,
  JobGetStatusResponse,
  PlaylistEditTrackPayload,
} from './types';
import { toast } from '@/components/ui/sonner';

class ApiClient {
  private baseUrlHttp: string;
  private baseUrlWs: string;
  private axiosInstance: AxiosInstance;

  constructor(config: {
    baseUrlHttp: string;
    baseUrlWs: string;
  }) {
    this.baseUrlHttp = config.baseUrlHttp;
    this.baseUrlWs = config.baseUrlWs;
    this.axiosInstance = axios.create({
      baseURL: this.baseUrlHttp,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle API errors
        const resStatus = error.response?.status ?? error.response?.statusText ?? '-';
        const resMessage = error.response?.data
          ? JSON.stringify(error.response?.data)
          : (error.message ?? 'No error message');
        const logText = `API Error! Status: ${resStatus}\n${resMessage}`;
        console.error(logText);
        toast.error(logText);
        return Promise.reject(error);
      }
    );
  }

  // ========== Health ==========

  getHealth() {
    return this.axiosInstance
      .get('/health')
      .then((res) => res.data);
  }

  // ========== Playlists ==========

  playlist_getAll() {
    return this.axiosInstance
      .get<DerivedPlaylist[]>('/playlists')
      .then((res) => res.data)
      .then((data) => {
        toast.info('Playlists loaded');
        return data;
      });
  }

  playlist_getOne({
    playlistId,
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
  }) {
    return this.axiosInstance
      .get<DerivedPlaylist>(`/playlists/${playlistId}`)
      .then((res) => res.data)
      .then((data) => {
        toast.info(`Playlist "${data.name}" loaded`);
        return data;
      });
  }

  playlist_spotify_refetch({
    playlistId,
    playlistName,
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    playlistName: DerivedPlaylist['name'];
  }) {
    return this.axiosInstance
      .post<boolean>(`/playlists/${playlistId}/spotify/refetch`)
      .then((res) => res.data)
      .then((data) => {
        toast.success(`Playlist "${playlistName}" (${playlistId}) updated - Spotify`);
        return data;
      });
  }

  playlist_updateTrack(payload: PlaylistEditTrackPayload) {
    return this.axiosInstance
      .post<void>(`/playlists/edit-track`, payload)
      .then((res) => res.data)
      .then((data) => {
        toast.success('Track updated');
        return data;
      });
  }

  playlist_youtube_autoSearchUrl({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    return this.axiosInstance
      .post<true>(`/playlists/${playlistId}/track/${trackId}/youtube/auto-search-url`)
      .then((res) => res.data)
      .then((data) => {
        toast.success('Track updated');
        return data;
      });
  }

  playlist_disk_getAudioFile({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    return this.axiosInstance
      .post<File>(this.playlist_disk_getAudioFile_BUILD_URL({ playlistId, trackId }))
      .then((res) => res.data)
      .then((data) => {
        toast.success('Track updated');
        return data;
      });
  }
  playlist_disk_getAudioFile_BUILD_URL({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    const path = `/playlists/${playlistId}/track/${trackId}/disk/get-audio-file`;
    return this.baseUrlHttp + path;
  }

  playlist_disk_deleteFile({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    return this.axiosInstance
      .post<boolean>(`/playlists/${playlistId}/track/${trackId}/disk/delete-file`)
      .then((res) => res.data)
      .then((data) => {
        toast.success('Track deleted');
        return data;
      });
  }

  playlist_disk_download({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    const loadingToast = toast.loading('Downloading track...');
    return this.axiosInstance
      .post<true>(`/playlists/${playlistId}/track/${trackId}/disk/download`)
      .then((res) => res.data)
      .then((data) => {
        toast.dismiss(loadingToast);
        toast.success('Track downloaded');
        return data;
      })
      .catch((error) => {
        toast.dismiss(loadingToast);
        return Promise.reject(error);
      });
  }

  playlist_disk_revealInFinder({
    playlistId,
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
  }) {
    return this.axiosInstance
      .post<true>(`/playlists/${playlistId}/disk/reveal-in-finder`)
      .then((res) => res.data);
  }

  jobGetStatus() {
    // NOTE: this is a websocket endpoint, axios does not support websockets
    const ws = new WebSocket(`${this.baseUrlWs}/playlists/ws/job-progress`);
    const responseDataType = {} as JobGetStatusResponse;
    return { ws, responseDataType };
  }

  // editPlaylist({
  //   playlistId,
  //   payload,
  // }: {
  //   playlistId: DerivedPlaylist['spotify_id'];
  //   payload: Partial<DerivedPlaylist>;
  // }) {
  //   return this.axiosInstance
  //     .post<DerivedPlaylist>(`/playlists/${playlistId}/edit`, payload)
  //     .then((res) => res.data);
  // }

  // ========== Downloads ==========

  // downloadTrack(request: DownloadRequest) {
  //   return this.axiosInstance
  //     .post('/download', request)
  //     .then((res) => res.data);
  // }

  // syncPlaylist(playlistId: string) {
  //   return this.axiosInstance
  //     .post(`/sync/${playlistId}`)
  //     .then((res) => res.data);
  // }

  // redownloadTrack(request: DownloadRequest) {
  //   return this.axiosInstance
  //     .post('/redownload', request)
  //     .then((res) => res.data);
  // }

  // deleteTrack(trackId: string, playlistId: string) {
  //   return this.axiosInstance
  //     .delete(`/tracks/${trackId}`, {
  //       params: { playlist_id: playlistId },
  //     })
  //     .then((res) => res.data);
  // }

  // ========== Metadata ==========

  // updateMetadata(request: EditMetadataRequest) {
  //   return this.axiosInstance
  //     .post(`/tracks/${request.track_id}/metadata`, request)
  //     .then((res) => res.data);
  // }

  // ========== ID3 Tags ==========

  // getID3Tags(trackId: string, playlistId: string) {
  //   return this.axiosInstance
  //     .get<ID3TagsResponse[]>(`/tracks/${trackId}/tags`, {
  //       params: { playlist_id: playlistId },
  //     })
  //     .then((res) => res.data);
  // }

  // updateID3Tags(request: ID3TagsUpdateRequest) {
  //   return this.axiosInstance
  //     .post(`/tracks/${request.track_id}/tags`, request)
  //     .then((res) => res.data);
  // }

  // ========== YouTube URLs ==========

  // setYoutubeUrl(request: EditYoutubeUrlRequest) {
  //   return this.axiosInstance
  //     .post(`/tracks/${request.track_id}/youtube-url`, request)
  //     .then((res) => res.data);
  // }

  // clearYoutubeUrl(trackId: string, playlistId: string) {
  //   return this.axiosInstance
  //     .delete(`/tracks/${trackId}/youtube-url`, {
  //       params: { playlist_id: playlistId },
  //     })
  //     .then((res) => res.data);
  // }

  // findYoutubeUrl(trackId: string, playlistId: string) {
  //   return this.axiosInstance
  //     .post(`/tracks/${trackId}/find-youtube`, {
  //       playlist_id: playlistId,
  //     })
  //     .then((res) => res.data);
  // }


}

export const apiClient = new ApiClient({
  baseUrlHttp: 'http://127.0.0.1:8000',
  baseUrlWs: 'ws://127.0.0.1:8000',
});
