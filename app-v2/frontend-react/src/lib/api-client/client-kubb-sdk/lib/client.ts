import axios, { type AxiosInstance } from 'axios';

// kubb
// import { createClient as kubbCreateClient } from "./generated/.kubb/client";
// import { client as kubbGlobalClient } from "./generated/.kubb/client";
import { ApiClientAxios as KubbApiOperations } from "./generated/client-axios/apiClientAxios";

// types
import { type DerivedTrack, type DerivedPlaylist } from './types.http';
import { schemaWsBackendEvent, type WsBackendEvent } from './types.ws';

import { toast } from '@/components/ui/sonner';


type ApiClientKubbSdk_InitOptions = {
  baseUrlHttp: string;
  baseUrlWs: string;
};

export class ApiClientKubbSdk {
  public apiHttp: ApiHttp;
  public apiWs: ApiWs;

  constructor(config: ApiClientKubbSdk_InitOptions) {
    this.apiHttp = new ApiHttp(config);
    this.apiWs = new ApiWs(config);
  }
}


class ApiHttp {
  private baseUrlHttp: string;
  private instanceAxios: AxiosInstance;
  public api: KubbApiOperations;

  constructor(config: ApiClientKubbSdk_InitOptions) {
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

    // init kubb client operations (kubb) linked to axios instance
    // NOTE: we edit the global kubb client (already instanced), that is used as fallback by kubb operations
    // kubbGlobalClient.setConfig({
    //   baseURL: this.baseUrlHttp,
    //   transport: this.instanceAxios,
    //   validateStatus: (status) => status >= 200 && status < 300,
    // });
    this.api = new KubbApiOperations({
      baseURL: this.baseUrlHttp,
      transport: this.instanceAxios,
      // throwOnError: true,
      // validateStatus: (status) => status >= 200 && status < 300,
    });
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

  constructor(config: ApiClientKubbSdk_InitOptions) {
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