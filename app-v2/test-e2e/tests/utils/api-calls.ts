import {
  expect,
  type Response as PlaywrightResponse,
} from "@playwright/test";

/**
 * Map of API endpoints configuration object used in tests
 */
export const API_ENDPOINTS = {
  PLAYLIST_GET_ALL: () => ({
    METHOD: 'GET',
    URL: `/playlists/`,
    RES_OK_STATUS: 200,
    RES_OK_BODY: [],
  } as const),
  PLAYLIST_CREATE: (playlistUrl: string) => ({
    METHOD: 'POST',
    URL: `/playlists/add`,
    REQ_OK_BODY: {
      playlistSpotifyUrl: playlistUrl,
    },
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Playlist added',
    RES_ERR_ALREADY_ADDED_STATUS: 500,
  } as const),
  PLAYLIST_GET_ONE: (id: string) => ({
    METHOD: 'GET',
    URL: `/playlists/${id}`,
    RES_OK_STATUS: 200,
    RES_ERR_NOT_FOUND_STATUS: 404,
  } as const),
  PLAYLIST_EDIT_ONE: (PLAYLIST_ID: string, NEW_PLAYLIST_DISK_DIR_NAME: string) => ({
    METHOD: 'POST',
    URL: `/playlists/edit-playlist`,
    REQ_OK_BODY: {
      playlist_id: PLAYLIST_ID,
      directory_name: NEW_PLAYLIST_DISK_DIR_NAME,
    },
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Playlist updated',
  } as const),
  PLAYLIST_DELETE_ONE: (id: string) => ({
    METHOD: 'DELETE',
    URL: `/playlists/${id}`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Playlist deleted',
  } as const),
  PLAYLIST_SPOTIFY_REFETCH: (id: string) => ({
    METHOD: 'POST',
    URL: `/playlists/${id}/spotify/refetch`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Playlist refetched (Spotify Side)',
  } as const),
  PLAYLIST_YOUTUBE_AUTO_SEARCH_URL_ALL_TRACKS: (id: string) => ({
    METHOD: 'POST',
    URL: `/playlists/${id}/youtube/auto-search-url`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Youtube Auto Search URL for all tracks scheduled',
  } as const),
  PLAYLIST_DISK_DOWNLOAD_ALL_TRACKS: (id: string) => ({
    METHOD: 'POST',
    URL: `/playlists/${id}/disk/download-all/job/start`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: "Download all tracks scheduled",
  } as const),
  PLAYLIST_DISK_DELETE_ORPHAN_TRACKS: (id: string) => ({
    METHOD: 'POST',
    URL: `/playlists/${id}/disk/delete-orphan-tracks`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: "Orphan tracks deleted",
  } as const),
  PLAYLIST_TRACK_YOUTUBE_AUTO_SEARCH_URL_SINGLE_TRACK: (playlistId: string, trackId: string) => ({
    METHOD: 'POST',
    URL: `/playlists/${playlistId}/track/${trackId}/youtube/auto-search-url`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Youtube Auto Search URL for single track OK',
  } as const),
  PLAYLIST_TRACK_EDIT_ONE: () => ({
    METHOD: 'POST',
    URL: `/edit-track`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Track updated',
  } as const),
  PLAYLIST_TRACK_DISK_DOWNLOAD: (playlistId: string, trackId: string) => ({
    METHOD: 'POST',
    URL: `/playlists/${playlistId}/track/${trackId}/disk/download`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: "Track downloaded",
  }),
  UTILS_DISK_REVEAL_PATH: () => ({
    METHOD: 'POST',
    URL: `/utils/disk/reveal-in-finder`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Disk folder revealed',
  } as const),
  SETTINGS_GET_SETTINGS: () => ({
    METHOD: 'GET',
    URL: `/settings/`,
    RES_OK_STATUS: 200,
  } as const),
  SETTINGS_UPDATE_SETTINGS: () => ({
    METHOD: 'PUT',
    URL: `/settings/`,
    RES_OK_STATUS: 200,
    RES_OK_TOAST_MSG: 'Settings updated',
  } as const),
};

type ApiEndpointConfig = ReturnType<typeof API_ENDPOINTS[keyof typeof API_ENDPOINTS]>;


/**
 * Filter function for `page.waitForResponse`.
 * @example
 * const API_CALL = API_ENDPOINTS.UTILS_DISK_REVEAL_PATH();
 * await page.waitForResponse(
 *   isThisHttpResponse(API_CALL)
 * );
 */
export function isThisHttpResponse(apiEndpointConfig: ApiEndpointConfig) {
  return (response: PlaywrightResponse) => {
    return (
      response.request().method() === apiEndpointConfig.METHOD
      &&
      response.url().includes(apiEndpointConfig.URL)
    );
  };
}

/**
 * Checker function that a playwright `Response` has the expected:
 * - `res status code`
 * - `res body (optional)`
 * - `req body (optional)`.
 * @example
 * const API_CALL = API_ENDPOINTS.UTILS_DISK_REVEAL_PATH();
 * 
 * const [response] = await Promise.all([
 *   page.waitForResponse(isThisHttpResponse(API_CALL)),
 *   page.getByRole('button', { name: 'Reveal' }).click(),
 * ]);
 * await checkHttpResponseState({
 *   response,
 *   resStatusCode: API_CALL.RES_OK_STATUS,
 *   resBody: API_CALL.RES_OK_TOAST_MSG,
 * })
 */
export async function checkHttpResponseState({
  response,
  reqBody,
  resStatusCode,
  resBody,
}: {
  response: PlaywrightResponse,
  reqBody?: Record<string, unknown>,
  resStatusCode: number,
  resBody?: Readonly<Record<string, unknown> | unknown[]>,
}) {

  // check request

  if (reqBody) {
    expect(response.request().postDataJSON()).toMatchObject(reqBody);
  }

  // check response

  expect(response.status()).toBe(resStatusCode);

  if (resBody) {
    expect(await response.json()).toEqual(resBody);
  }

}