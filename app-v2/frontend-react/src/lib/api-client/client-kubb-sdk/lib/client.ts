import axios, { HttpStatusCode, type AxiosInstance } from 'axios';

// kubb
// import { createClient as kubbCreateClient } from "./generated/.kubb/client";
// import { client as kubbGlobalClient } from "./generated/.kubb/client";
import { ApiClientAxios as KubbApiOperations } from "./generated/client-axios/apiClientAxios";

// types
import { type DerivedTrack, type DerivedPlaylist } from './types.http';
import { schemaWsBackendEvent, type WsBackendEvent } from './types.ws';

import { toast } from '@/components/ui/sonner';
import { ToastPresetHttpRequestError } from '#/components/ui/sonner.extra';


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

        // get HTTP request/response data
        const resCommunicationStatus = error.response?.status ? 'OK' : 'ERROR';
        const resHTTPStatus = error.response?.status ? Number(error.response?.status) : '-';
        const resHTTPMessage = error.response?.data ? JSON.stringify(error.response?.data, null, 2) : (error.message ?? 'No error message');

        // log
        console.error(
          `API Error\nHTTP Status: ${resCommunicationStatus}\nHTTP Code: ${resHTTPStatus}\n${resHTTPMessage}`,
          error
        );
        //  toast
        toast.error(
          ToastPresetHttpRequestError({
            title: 'API Error',
            httpRequestStatus: resCommunicationStatus,
            httpStatusCode: resHTTPStatus,
            message: resHTTPMessage,
          }),
        );

        // rethrow
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