import axios, { type AxiosInstance } from 'axios';

import {
  type DerivedPlaylist,
  type DerivedTrack,
  type PlaylistEditTrackPayload,
  type PlaylistRaw,
  type Settings,
} from './types.http';
import {
  schemaWsBackendEvent,
  type WsBackendEvent,
} from './types.ws';

import { toast } from '@/components/ui/sonner';

type ApiClientManual_InitOptions = {
  baseUrlHttp: string;
  baseUrlWs: string;
};

export class ApiClientManual {
  public apiHttp: ApiHttp;
  public apiWs: ApiWs;

  constructor(config: ApiClientManual_InitOptions) {
    this.apiHttp = new ApiHttp(config);
    this.apiWs = new ApiWs(config);
  }
}

class ApiHttp {
  private baseUrlHttp: string;
  private axiosInstance: AxiosInstance;

  constructor(config: ApiClientManual_InitOptions) {
    this.baseUrlHttp = config.baseUrlHttp;
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
        const logText = `API Error!\nHTTP Status: ${resStatus}\n${resMessage}`;
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

  playlistAddOne({
    playlistSpotifyUrl,
  }: {
    playlistSpotifyUrl: string;
  }) {
    return this.axiosInstance
      .post<true>('/playlists/add', { playlistSpotifyUrl })
      .then((res) => res.data)
      .then((data) => {
        toast.success('Playlist added');
        return data;
      });
  }

  playlistGetAll() {
    return this.axiosInstance
      .get<PlaylistRaw[]>('/playlists/')
      .then((res) => res.data);
    // .then((data) => {
    //   toast.info('Playlists loaded');
    //   return data;
    // });
  }

  playlistGetOne({
    playlistId,
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
  }) {
    return this.axiosInstance
      .get<DerivedPlaylist>(`/playlists/${playlistId}`)
      .then((res) => res.data);
    // .then((data) => {
    //   toast.info(`Playlist "${data.name}" loaded`);
    //   return data;
    // });
  }

  playlistSpotifyRefetch({
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

  playlistEditTrack(payload: PlaylistEditTrackPayload) {
    return this.axiosInstance
      .post<void>(`/playlists/edit-track`, payload)
      .then((res) => res.data)
      .then((data) => {
        toast.success('Track updated');
        return data;
      });
  }

  playlistYoutubeAutoSearchUrlSingleTrack({
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

  playlistYoutubeAutoSearchUrlAllTracks({
    playlistId,
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
  }) {
    return this.axiosInstance
      .post<true>(`/playlists/${playlistId}/youtube/auto-search-url`)
      .then((res) => res.data);
  }

  playlistDiskGetAudioFile({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    return this.axiosInstance
      .post<File>(this.playlistDiskGetAudioFile_BUILD_URL({ playlistId, trackId }))
      .then((res) => res.data)
      .then((data) => {
        toast.success('Track updated');
        return data;
      });
  }

  playlistDiskGetAudioFile_BUILD_URL({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    const path = `/playlists/${playlistId}/track/${trackId}/disk/get-audio-file`;
    return this.baseUrlHttp + path;
  }

  playlistDiskDeleteFile({
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

  playlistDiskDownloadSingleTrack({
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

  playlistDiskDownloadAllTracks({
    playlistId,
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
  }) {
    return this.axiosInstance
      .post<true>(`/playlists/${playlistId}/disk/download-all/job/start`)
      .then((res) => res.data);
  }


  // ========== Settings ==========

  settingsGetSettings() {
    return this.axiosInstance
      .get<Settings>(`/settings/`)
      .then((res) => res.data);
  }

  settingsUpdateSettings(payload: Settings['mutable']) {
    return this.axiosInstance
      .put<boolean>(`/settings/`, payload)
      .then((res) => res.data);
  }

  // ========== Demo ==========

  demoJobDemoStart() {
    return this.axiosInstance
      .post<true>('/demo/job-demo/start')
      .then((res) => res.data);
  }

  // ========== Utils ==========

  utilsDiskRevealInFinder(payload: {
    path: string;
  }) {
    return this.axiosInstance
      .post<true>('/utils/disk/reveal-in-finder', payload)
      .then((res) => res.data);
  }

}

class ApiWs {
  private baseUrlWs: string;

  constructor(config: ApiClientManual_InitOptions) {
    this.baseUrlWs = config.baseUrlWs;
  }

  wsEntryPointConnect() {
    return {
      getWs: () => new WebSocket(`${this.baseUrlWs}/ws/entry-point`),
      _responseDataSchema: schemaWsBackendEvent,
      _responseDataType: {} as WsBackendEvent
    };
  }

}
