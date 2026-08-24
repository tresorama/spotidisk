import axios, { type AxiosInstance } from 'axios';

// kubb
import { client as kubbGlobalClient } from "./generated/.kubb/client";
import * as kubbGlobalApiOperations from "./generated/client-axios";

// types
import { type DerivedTrack, type DerivedPlaylist } from './types.http';
import { schemaWsBackendEvent, type WsBackendEvent } from './types.ws';

import { toast } from '@/components/ui/sonner';


type ApiClientKubbFns_InitOptions = {
  baseUrlHttp: string;
  baseUrlWs: string;
};

export class ApiClientKubbFns {
  public apiHttp: ApiHttp;
  public apiWs: ApiWs;

  constructor(config: ApiClientKubbFns_InitOptions) {
    this.apiHttp = new ApiHttp(config);
    this.apiWs = new ApiWs(config);
  }
}


class ApiHttp {
  private baseUrlHttp: string;
  private instanceAxios: AxiosInstance;
  private instanceCoreClient: typeof kubbGlobalClient;
  public api: typeof kubbGlobalApiOperations;

  constructor(config: ApiClientKubbFns_InitOptions) {
    this.baseUrlHttp = config.baseUrlHttp;

    // init axios instance
    this.instanceAxios = axios.create({
      baseURL: this.baseUrlHttp,
      // headers: {
      //   'Content-Type': 'application/json',
      // },
    });
    this.instanceAxios.interceptors.response.use(
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

    // add axios instance as fetch client to kubb client
    // NOTE: kubb surface api is plit into client and operations
    // NOTE: kubb client is a global singlton already instanced
    // NOTE: kubb operations are functions that can reciev a client "per-call" that fallback to the global one
    this.instanceCoreClient = kubbGlobalClient;
    this.instanceCoreClient.setConfig({
      baseURL: this.baseUrlHttp,
      transport: this.instanceAxios,
      // throwOnError: true,
      // validateStatus: (status) => status >= 200 && status < 300,
    });
    this.api = kubbGlobalApiOperations;
  }

  getUrl__playlist_disk_getAudioFile({
    playlistId,
    trackId
  }: {
    playlistId: DerivedPlaylist['spotify_id'];
    trackId: DerivedTrack['spotify_id'];
  }) {
    const path = `/playlists/${playlistId}/track/${trackId}/disk/get-audio-file`;
    return this.baseUrlHttp + path;
  }
}

class ApiWs {
  private baseUrlWs: string;
  constructor(config: ApiClientKubbFns_InitOptions) {
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