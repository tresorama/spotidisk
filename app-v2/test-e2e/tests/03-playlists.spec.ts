import { test, expect } from '@playwright/test';
import { CONSTANTS } from '../constants';
import { API_ENDPOINTS, checkHttpResponseState, isThisHttpResponse } from './utils/api-calls';
import { waitForToast } from './utils/toast';
import { sleep } from '../utils/sleep';

const { FRONTEND_URL } = CONSTANTS;
const PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE = (() => {
  const playlistId = '120OxtOIOAVjA1Fh3zMSVm';
  return {
    id: playlistId,
    url: `https://open.spotify.com/playlist/${playlistId}`,
  };
})();
const PUBLIC_SPOTIFY_PLAYLIST_NOT_EXISTING = (() => {
  const playlistId = 'FAKE_PLAYLIST_ID';
  return {
    id: playlistId,
  };
})();

// init tests

test.use({
  baseURL: FRONTEND_URL,
});

// run tests

test.describe.serial('ordered tests', () => {


  test.describe.serial('check app state on first launch', () => {

    test('check sidebar playlists items count - should be empty at start', async ({ page }) => {
      const API_CALL = API_ENDPOINTS.PLAYLIST_GET_ALL();

      // go to /
      // listen response
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        page.goto('/'),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
        resBody: API_CALL.RES_OK_BODY,
      });

      // check request result - DOM
      const elSidebarPlaylistList = page.getByLabel('Sidebar Group Playlists List');
      await expect(elSidebarPlaylistList).toHaveAttribute('data-items-count', '0');
    });

  });

  test.describe.serial('Playlist creation and delete flow', () => {

    test('create playlist, check that is added, then recreate it and expect error', async ({ page }) => {
      const PLAYLIST_URL = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.url;
      const API_CALL_PLAYLIST_CREATE = API_ENDPOINTS.PLAYLIST_CREATE(PLAYLIST_URL);

      // 1. go to /
      await page.goto('/');

      // 2. go to /add-playlist
      await page
        .getByLabel('Sidebar Footer')
        .getByRole('button', { name: 'Add Playlist' })
        .click();
      await page.waitForURL('**/add-playlist');

      // 3. add playlist (first time)

      // get current state
      const elSidebarPlaylistList = page.getByLabel('Sidebar Group Playlists List');
      const oldPlaylistCount = Number(await elSidebarPlaylistList.getAttribute('data-items-count'));

      // get form els
      const elForm = page.getByRole('form', { name: 'Form Playlist Add', exact: true });
      const elInputPlaylistSpotifyUrl = elForm.getByRole('textbox', { name: 'Playlist Spotify URL' });
      const elSubmitButton = elForm.getByRole('button', { name: 'Add Playlist' });

      // fill the form
      await expect(elForm).toBeVisible();
      await expect(elInputPlaylistSpotifyUrl).toBeVisible();
      await expect(elSubmitButton).toBeVisible();
      await elInputPlaylistSpotifyUrl.fill(PLAYLIST_URL);

      // submit form
      const [response1] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_PLAYLIST_CREATE)),
        elSubmitButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response: response1,
        reqBody: API_CALL_PLAYLIST_CREATE.REQ_OK_BODY,
        resStatusCode: API_CALL_PLAYLIST_CREATE.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_PLAYLIST_CREATE.RES_OK_TOAST_MSG });

      const newExpectedPlaylistCount = oldPlaylistCount + 1;
      await expect(elSidebarPlaylistList).toHaveAttribute('data-items-count', newExpectedPlaylistCount.toString());

      // 4. add playlist (second time)

      // trigger the same request
      const [response2] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_PLAYLIST_CREATE)),
        elSubmitButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response: response2,
        reqBody: API_CALL_PLAYLIST_CREATE.REQ_OK_BODY,
        resStatusCode: API_CALL_PLAYLIST_CREATE.RES_ERR_ALREADY_ADDED_STATUS,
      });

      // check request result - DOM
      await waitForToast.errorHttpRequest({ page, httpStatusCode: API_CALL_PLAYLIST_CREATE.RES_ERR_ALREADY_ADDED_STATUS });

      await expect(elSidebarPlaylistList).toHaveAttribute('data-items-count', newExpectedPlaylistCount.toString());
    });

    test('that /playlist/{playlistId} with fake id is NOT FOUND', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_NOT_EXISTING.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_GET_ONE(PLAYLIST_ID);

      // go to /playlist/{playlistId} page
      // listen response
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        page.goto(`/playlist/${PLAYLIST_ID}`),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_ERR_NOT_FOUND_STATUS,
      });

      // check request result - DOM

      const elH1 = page.getByRole('heading', { level: 1, name: 'Error loading playlist', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });
      await expect(elH1).toHaveText('Error loading playlist');
      await expect(elH1).toHaveAttribute('data-playlist-id', PLAYLIST_ID);
      await expect(elH1).toHaveAttribute('data-playlist-fetch-status', 'ERROR_OR_NOT_FOUND');

      const elAlert = page.getByRole('alert', { name: 'Error loading playlist', exact: true });
      await expect(elAlert).toHaveAttribute('data-playlist-id', PLAYLIST_ID);

      await waitForToast.errorHttpRequest({ page, httpStatusCode: API_CALL.RES_ERR_NOT_FOUND_STATUS });
    });

    test('that /playlist/{playlistId} with existing playlist is FOUND', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_GET_ONE(PLAYLIST_ID);

      // go to /playlist/{playlistId} page
      // listen response
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        page.goto(`/playlist/${PLAYLIST_ID}`),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check request result - DOM

      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });
      await expect(elH1).toHaveAttribute('data-playlist-id', PLAYLIST_ID);
      await expect(elH1).toHaveAttribute('data-playlist-fetch-status', 'FOUND');

      const elPlaylistActions = page.getByLabel('Playlist Actions', { exact: true });
      await expect(elPlaylistActions).toBeVisible();

      const elPlaylistActionsSpotify = elPlaylistActions.getByLabel('Playlist Actions Spotify', { exact: true });
      const elPlaylistActionsSpotifyName = elPlaylistActionsSpotify.getByLabel('Spotify Playlist Name', { exact: true });
      const elPlaylistActionsSpotifyId = elPlaylistActionsSpotify.getByLabel('Spotify Playlist ID', { exact: true });
      const elPlaylistActionsSpotifyButtonRefetch = elPlaylistActionsSpotify.getByRole('button', { name: 'Refetch playlist data from Spotify', exact: true });
      const elPlaylistActionsSpotifyButtonView = elPlaylistActionsSpotify.getByRole('button', { name: 'View the playlist on Spotify in a new tab', exact: true });
      await expect(elPlaylistActionsSpotify).toBeVisible();
      await expect(elPlaylistActionsSpotifyName).toBeVisible();
      await expect(elPlaylistActionsSpotifyId).toBeVisible();
      await expect(elPlaylistActionsSpotifyId).toHaveText(PLAYLIST_ID);
      await expect(elPlaylistActionsSpotifyButtonRefetch).toBeVisible();
      await expect(elPlaylistActionsSpotifyButtonView).toBeVisible();

      const elPlaylistActionsYoutube = elPlaylistActions.getByLabel('Playlist Actions Youtube', { exact: true });
      const elPlaylistActionsYoutubeButtonAutoSearch = elPlaylistActionsYoutube.getByRole('button', { name: `Run Youtube 'Auto-Search URL' for all tracks`, exact: true });
      await expect(elPlaylistActionsYoutube).toBeVisible();
      await expect(elPlaylistActionsYoutubeButtonAutoSearch).toBeVisible();

      const elPlaylistActionsDisk = elPlaylistActions.getByLabel('Playlist Actions Disk', { exact: true });
      const elPlaylistActionsDiskButtonRename = elPlaylistActionsDisk.getByRole('button', { name: 'Update the directory name of the playlist folder on your computer', exact: true });
      const elPlaylistActionsDiskButtonReveal = elPlaylistActionsDisk.getByRole('button', { name: 'Open playlist folder on your computer', exact: true });
      const elPlaylistActionsDiskButtonDownloadAll = elPlaylistActionsDisk.getByRole('button', { name: 'Download all missing tracks of this playlist', exact: true });
      const elPlaylistActionsDiskButtonDeleteOrphans = elPlaylistActionsDisk.getByRole('button', { name: 'Delete orphan files in the playlist folder', exact: true });
      await expect(elPlaylistActionsDisk).toBeVisible();
      await expect(elPlaylistActionsDiskButtonRename).toBeVisible();
      await expect(elPlaylistActionsDiskButtonReveal).toBeVisible();
      await expect(elPlaylistActionsDiskButtonDownloadAll).toBeVisible();
      await expect(elPlaylistActionsDiskButtonDeleteOrphans).toBeVisible();

      const elPlaylistTracksTable = page.getByLabel('Playlist Tracks Table', { exact: true });
      await expect(elPlaylistTracksTable).toBeVisible();

    });

    test('delete playlist and check sidebar playlists - should be less one', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_DELETE_ONE(PLAYLIST_ID);

      // go to playlist page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // get current number of playlist
      const elSidebarPlaylistList = page.getByLabel('Sidebar Group Playlists List');
      await expect(elSidebarPlaylistList).toBeVisible();
      const oldPlaylistCount = Number(await elSidebarPlaylistList.getAttribute('data-items-count'));

      // trigger operation
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        // - open dropdown of first sidebar playlist item
        elSidebarPlaylistList
          .getByRole('listitem').first()
          .getByRole('button', { name: 'Playlist Options' }).click(),
        // - click "Delete"
        page.getByRole('menuitem', { name: 'Delete Playlist' }).click(),
        // - click confirm in dialog
        page.getByRole('button', { name: 'Delete Playlist' }).click(),
      ]);

      // check mutation result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check mutation result - frontend redirect to /
      await page.waitForURL(`/`);

      // check mutation result - DOM 

      await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

      const newExpectedPlaylistCount = oldPlaylistCount - 1;
      await expect(elSidebarPlaylistList).toHaveAttribute('data-items-count', newExpectedPlaylistCount.toString());
    });

  });

  test.describe.serial('Playlist actions', () => {

    // create playlist

    test('create playlist for rest of tests', async ({ page }) => {
      const PLAYLIST_URL = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.url;
      const API_CALL_PLAYLIST_CREATE = API_ENDPOINTS.PLAYLIST_CREATE(PLAYLIST_URL);

      // 1. go to /
      await page.goto('/');

      // 2. go to /add-playlist
      await page
        .getByLabel('Sidebar Footer')
        .getByRole('button', { name: 'Add Playlist' })
        .click();
      await page.waitForURL('**/add-playlist');

      // 3. triggr create playlist (first time)

      // get form els
      const elForm = page.getByRole('form', { name: 'Form Playlist Add', exact: true });
      const elInputPlaylistSpotifyUrl = elForm.getByRole('textbox', { name: 'Playlist Spotify URL' });
      const elSubmitButton = elForm.getByRole('button', { name: 'Add Playlist' });

      // fill the form
      await expect(elForm).toBeVisible();
      await expect(elInputPlaylistSpotifyUrl).toBeVisible();
      await expect(elSubmitButton).toBeVisible();
      await sleep(2000);
      await elInputPlaylistSpotifyUrl.fill(PLAYLIST_URL);

      // submit form
      const [response1] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_PLAYLIST_CREATE)),
        elSubmitButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response: response1,
        reqBody: API_CALL_PLAYLIST_CREATE.REQ_OK_BODY,
        resStatusCode: API_CALL_PLAYLIST_CREATE.RES_OK_STATUS,
      });

      // check request result - DOM
      await waitForToast.success({ page, partialText: API_CALL_PLAYLIST_CREATE.RES_OK_TOAST_MSG });

    });


    // test playlist actions part 1

    test('that /playlist/{playlistId} playlist action SPOTIFY_REFETCH is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_SPOTIFY_REFETCH(PLAYLIST_ID);

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // trigger operation
      const elButton = page
        .getByLabel('Playlist Actions', { exact: true })
        .getByRole('button', { name: 'Refetch playlist data from Spotify', exact: true });
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        elButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

    });

    // test track actions

    test('that /playlist/{playlistId} first track has spotify data but no youtub and no disk data', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // get first track data
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();

      // get els
      await expect(elFirstTrack).toBeVisible();

      await expect(elFirstTrack.getByLabel('song')).toBeVisible();
      await expect(elFirstTrack.getByLabel('song').getByLabel('Track Title')).toBeVisible();
      await expect(elFirstTrack.getByLabel('song').getByLabel('Track Artists')).toBeVisible();
      await expect(elFirstTrack.getByLabel('song').getByLabel('Track Album')).toBeVisible();
      await expect(elFirstTrack.getByLabel('song').getByLabel('Track Label')).toBeVisible();

      await expect(elFirstTrack.getByLabel('spotify').getByRole('button', { name: 'Open track in Spotify' })).toBeVisible();
      await expect(elFirstTrack.getByLabel('spotify').getByLabel('Spotify Duration')).toBeVisible();
      await expect(elFirstTrack.getByLabel('spotify').getByRole('button', { name: 'Open audio preview in Spotify' })).toBeVisible();

      await expect(elFirstTrack.getByLabel('youtube').getByLabel('Youtube Track Link Status')).toBeVisible();
      await expect(elFirstTrack.getByLabel('youtube').getByLabel('Youtube Track Link Status')).toContainText('No Youtube track is linked');
      await expect(elFirstTrack.getByLabel('youtube').getByRole('button', { name: 'Do Auto Search URL for this track' })).toBeVisible();
      await expect(elFirstTrack.getByLabel('youtube').getByRole('button', { name: 'Open Manual Search for this track' })).toBeVisible();
      await expect(elFirstTrack.getByLabel('youtube').getByRole('button', { name: 'Open track in YouTube' })).not.toBeVisible();
      await expect(elFirstTrack.getByLabel('youtube').getByRole('button', { name: 'Set/Update YouTube URL' })).toBeVisible();
      await expect(elFirstTrack.getByLabel('youtube').getByRole('button', { name: 'Clear YouTube URL for this track' })).not.toBeVisible();
      await expect(elFirstTrack.getByLabel('youtube').getByRole('button', { name: 'Copy YouTube URL for this track to clipboard' })).not.toBeVisible();
    });

    test('that /playlist/{playlistId} first track action SPOTIFY_PREVIEW is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // get els
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();
      const elButtonDialogTrigger = elFirstTrack
        .getByLabel('spotify')
        .getByRole('button', { name: 'Open audio preview in Spotify' });

      // trigger action
      await expect(elFirstTrack).toBeVisible();
      await expect(elButtonDialogTrigger).toBeVisible();
      await elButtonDialogTrigger.click();

      // check request result - DOM
      const elDialog = page.getByRole('dialog', { name: 'Spotify Track Preview', exact: true });
      await expect(elDialog).toBeVisible();
    });

    test('that /playlist/{playlistId} first track action YOUTUBE_SET_URL and YOUTUBE_CLEAR_URL is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL_EDIT_TRACK = API_ENDPOINTS.PLAYLIST_TRACK_EDIT_ONE();
      const NEW_YOUTUBE_URL = 'https://www.youtube.com/watch?v=QH2_TGUlwu4';

      // 1. go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // 2. check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // 3. get els
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();
      await expect(elFirstTrack).toBeVisible();

      // 4. set youtube url

      // ensure that the first track has no youtube link
      const elYoutubeLinkStatus = elFirstTrack.getByLabel('Youtube Track Link Status');
      await expect(elYoutubeLinkStatus).toBeVisible();
      await expect(elYoutubeLinkStatus).toContainText('No Youtube track is linked');

      // open dialog
      const elDialogTrigger = elFirstTrack.getByRole('button', { name: 'Set/Update YouTube URL', exact: true });
      await elDialogTrigger.click();

      // get form els
      const elDialog = page.getByRole('dialog', { name: 'Set Youtube URL Manually' });
      const elForm = elDialog.getByRole('form');
      const elInputUrl = elForm.getByRole('textbox', { name: 'YouTube URL' });
      const elSubmitButton = elForm.getByRole('button', { name: 'Update' });
      await expect(elDialog).toBeVisible();
      await expect(elForm).toBeVisible();
      await expect(elInputUrl).toBeVisible();
      await expect(elSubmitButton).toBeVisible();

      // fill the form
      await elInputUrl.fill(NEW_YOUTUBE_URL);

      // trigger operation
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_EDIT_TRACK)),
        elSubmitButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL_EDIT_TRACK.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_EDIT_TRACK.RES_OK_TOAST_MSG });

      await expect(elDialog).not.toBeVisible();

      await expect(elYoutubeLinkStatus).toContainText('A Youtube track is linked');

      // 5. clear youtube url

      // trigger operation
      const elButtonClearYoutubeUrl = elFirstTrack.getByRole('button', { name: 'Clear YouTube URL for this track', exact: true });
      const [response2] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_EDIT_TRACK)),
        elButtonClearYoutubeUrl.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response: response2,
        resStatusCode: API_CALL_EDIT_TRACK.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_EDIT_TRACK.RES_OK_TOAST_MSG });

      await expect(elYoutubeLinkStatus).toContainText('No Youtube track is linked');

    });

    test('that /playlist/{playlistId} first track action YOUTUBE_AUTO_SEARCH_URL is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;

      // 1. go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // 2. check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // 3. check current status

      // get first track
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();
      await expect(elFirstTrack).toBeVisible();

      // get track id
      const elFirstTrackTrackData = elFirstTrack.getByLabel('Track Data', { exact: true });
      const TRACK_ID = await elFirstTrackTrackData.getAttribute('data-track-id');
      expect(TRACK_ID).toBeDefined();
      expect(TRACK_ID.length).toBeGreaterThan(0);

      // ensure that the first track has no youtube link
      const elYoutubeLinkStatus = elFirstTrack.getByLabel('Youtube Track Link Status');
      await expect(elYoutubeLinkStatus).toBeVisible();
      await expect(elYoutubeLinkStatus).toContainText('No Youtube track is linked');

      // 4. do auto search youtube url
      const elButton = elFirstTrack.getByRole('button', { name: 'Do Auto Search URL for this track', exact: true });
      const API_CALL_YOUTUBE_AUTO_SEARCH = API_ENDPOINTS.PLAYLIST_TRACK_YOUTUBE_AUTO_SEARCH_URL_SINGLE_TRACK(PLAYLIST_ID, TRACK_ID);
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_YOUTUBE_AUTO_SEARCH)),
        elButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL_YOUTUBE_AUTO_SEARCH.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_YOUTUBE_AUTO_SEARCH.RES_OK_TOAST_MSG });

      await expect(elYoutubeLinkStatus).toContainText('A Youtube track is linked');

    });

    test('that /playlist/{playlistId} first track action YOUTUBE_AUDIO_PREVIEW is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // get els
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();
      const elDialogTrigger = elFirstTrack.getByRole('button', { name: 'Open track in YouTube' });

      // open dialog
      await expect(elFirstTrack).toBeVisible();
      await elDialogTrigger.click();

      // get form els
      const elDialog = page.getByRole('dialog', { name: 'YouTube Track Preview' });
      await expect(elDialog).toBeVisible();

    });

    test('that /playlist/{playlistId} first track action DISK_DOWNLOAD is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // get els
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();
      await expect(elFirstTrack).toBeVisible();

      // get track id
      const elFirstTrackTrackData = elFirstTrack.getByLabel('Track Data', { exact: true });
      const TRACK_ID = await elFirstTrackTrackData.getAttribute('data-track-id');
      expect(TRACK_ID).toBeDefined();
      expect(TRACK_ID.length).toBeGreaterThan(0);

      // ensure that the first track has youtube link
      const elYoutubeLinkStatus = elFirstTrack.getByLabel('Youtube Track Link Status');
      await expect(elYoutubeLinkStatus).toContainText('A Youtube track is linked');

      // trigger operation
      const elButtonDownload = elFirstTrack.getByRole('button', { name: 'Download/Re-download track from YouTube', exact: true });
      const API_CALL_DISK_DOWNLOAD = API_ENDPOINTS.PLAYLIST_TRACK_DISK_DOWNLOAD(PLAYLIST_ID, TRACK_ID);
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_DISK_DOWNLOAD), { timeout: 3 * 60 * 1000 }),
        elButtonDownload.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL_DISK_DOWNLOAD.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_DISK_DOWNLOAD.RES_OK_TOAST_MSG });

      const elDiskLinkStatus = elFirstTrack.getByLabel('Disk Track Link Status');
      await expect(elDiskLinkStatus).toContainText('File on disk present/ already downloaded');

    });

    test('that /playlist/{playlistId} first track action DISK_PREVIEW is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // get els
      const elFirstTrack = page
        .getByLabel('Playlist Tracks Table', { exact: true })
        .getByRole('rowgroup', { name: "Table Body" })
        .getByRole('row').first();
      await expect(elFirstTrack).toBeVisible();

      // get track id
      const elFirstTrackTrackData = elFirstTrack.getByLabel('Track Data', { exact: true });
      const TRACK_ID = await elFirstTrackTrackData.getAttribute('data-track-id');
      expect(TRACK_ID).toBeDefined();
      expect(TRACK_ID.length).toBeGreaterThan(0);

      // ensure that the first track has disk link
      const elYoutubeLinkStatus = elFirstTrack.getByLabel('Disk Track Link Status');
      await expect(elYoutubeLinkStatus).toContainText('File on disk present/ already downloaded');

      // trigger operation
      const elDialogTrigger = elFirstTrack.getByRole('button', { name: 'Play downloaded track from disk', exact: true });
      await elDialogTrigger.click();

      // check DOM
      const elDialog = page.getByRole('dialog', { name: 'Disk Track Preview' });
      await expect(elDialog).toBeVisible();


    });

    test('that /playlist/{playlistId} playlist action YOUTUBE_AUTO_SEARCH_URL_ALL_TRACKS is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_YOUTUBE_AUTO_SEARCH_URL_ALL_TRACKS(PLAYLIST_ID);

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // trigger operation
      const elButton = page
        .getByLabel('Playlist Actions', { exact: true })
        .getByRole('button', { name: `Run Youtube 'Auto-Search URL' for all tracks`, exact: true });
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        elButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

    });

    // test playlist actions part 2

    test('that /playlist/{playlistId} playlist action DISK_RENAME_FOLDER is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const NEW_PLAYLIST_DISK_DIR_NAME = 'new-folder-name';
      const API_CALL_PLAYLIST_EDIT = API_ENDPOINTS.PLAYLIST_EDIT_ONE(PLAYLIST_ID, NEW_PLAYLIST_DISK_DIR_NAME);
      const API_CALL_PLAYLIST_GET_ONE = API_ENDPOINTS.PLAYLIST_GET_ONE(PLAYLIST_ID);

      // go to /playlist/{playlistId} page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // open dialog
      const elDialogTriggerDiskRenameFolder = page
        .getByLabel('Playlist Actions Disk', { exact: true })
        .getByRole('button', { name: `Update the directory name of the playlist folder on your computer`, exact: true });
      await expect(elDialogTriggerDiskRenameFolder).toBeVisible();
      await elDialogTriggerDiskRenameFolder.click();

      // get form els
      const elDialog = page.getByRole('dialog', { name: 'Rename the playlist folder on your computer' });
      const elForm = elDialog.getByRole('form');
      const elInputNewFolderName = elForm.getByRole('textbox', { name: 'Directory Name' });
      const elSubmitButton = elForm.getByRole('button', { name: 'Update' });

      // fill the form
      await expect(elDialog).toBeVisible();
      await expect(elForm).toBeVisible();
      await expect(elInputNewFolderName).toBeVisible();
      await expect(elSubmitButton).toBeVisible();
      await elInputNewFolderName.fill(NEW_PLAYLIST_DISK_DIR_NAME);

      // submit form + listen for response
      const [
        responseGetOne,
        responseEdit,
      ] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_PLAYLIST_GET_ONE)),
        page.waitForResponse(isThisHttpResponse(API_CALL_PLAYLIST_EDIT)),
        elSubmitButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response: responseEdit,
        reqBody: API_CALL_PLAYLIST_EDIT.REQ_OK_BODY,
        resStatusCode: API_CALL_PLAYLIST_EDIT.RES_OK_STATUS,
      });
      await checkHttpResponseState({
        response: responseGetOne,
        resStatusCode: API_CALL_PLAYLIST_GET_ONE.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_PLAYLIST_EDIT.RES_OK_TOAST_MSG });

      const elPlaylistDiskDirName = page
        .getByLabel('Playlist Actions Disk', { exact: true })
        .getByLabel('Playlist Disk Directory Name', { exact: true });
      await expect(elPlaylistDiskDirName).toBeVisible();
      await expect(elPlaylistDiskDirName).toHaveText(NEW_PLAYLIST_DISK_DIR_NAME);

    });

    test('that /playlist/{playlistId} playlist action DISK_REVEAL_FOLDER is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.UTILS_DISK_REVEAL_PATH();

      // go to playlist page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // trigger operation
      const elButton = page
        .getByLabel('Playlist Actions', { exact: true })
        .getByRole('button', { name: `Open playlist folder on your computer`, exact: true });
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        elButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

    });

    test('that /playlist/{playlistId} playlist action DISK_DELETE_ORPHANS is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL_PLAYLIST_DELETE_ORPHANS = API_ENDPOINTS.PLAYLIST_DISK_DELETE_ORPHAN_TRACKS(PLAYLIST_ID);

      // go to playlist page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // trigger operation
      const elButton = page
        .getByLabel('Playlist Actions Disk', { exact: true })
        .getByRole('button', { name: `Delete orphan files in the playlist folder`, exact: true });
      await expect(elButton).toBeVisible();
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL_PLAYLIST_DELETE_ORPHANS)),
        elButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL_PLAYLIST_DELETE_ORPHANS.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL_PLAYLIST_DELETE_ORPHANS.RES_OK_TOAST_MSG });

    });

    test('that /playlist/{playlistId} playlist action DISK_DOWNLOAD_ALL is working', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_DISK_DOWNLOAD_ALL_TRACKS(PLAYLIST_ID);

      // go to playlist page
      await page.goto(`/playlist/${PLAYLIST_ID}`);

      // check that page is for a FOUND page
      const elH1 = page.getByRole('heading', { level: 1, name: 'Playlist Title', exact: true });
      await expect(elH1).toBeVisible({ timeout: 20 * 1000 });

      // trigger operation
      const elButton = page
        .getByLabel('Playlist Actions', { exact: true })
        .getByRole('button', { name: `Download all missing tracks of this playlist`, exact: true });
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        elButton.click(),
      ]);

      // check request result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check request result - DOM

      await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

    });

    // delete
    test('delete playlist', async ({ page }) => {
      const PLAYLIST_ID = PUBLIC_SPOTIFY_PLAYLIST_TO_CREATE.id;
      const API_CALL = API_ENDPOINTS.PLAYLIST_DELETE_ONE(PLAYLIST_ID);

      // go to playlist page
      await page.goto(`/`);

      // get current number of playlist

      // trigger operation
      const elSidebarPlaylistList = page.getByLabel('Sidebar Group Playlists List');
      const [response] = await Promise.all([
        page.waitForResponse(isThisHttpResponse(API_CALL)),
        // - open dropdown of first sidebar playlist item
        elSidebarPlaylistList
          .getByRole('listitem').first()
          .getByRole('button', { name: 'Playlist Options' }).click(),
        // - click "Delete"
        page.getByRole('menuitem', { name: 'Delete Playlist' }).click(),
        // - click confirm in dialog
        page.getByRole('button', { name: 'Delete Playlist' }).click(),
      ]);

      // check mutation result - network
      await checkHttpResponseState({
        response,
        resStatusCode: API_CALL.RES_OK_STATUS,
      });

      // check mutation result - DOM 

      await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

    });


  });

});
