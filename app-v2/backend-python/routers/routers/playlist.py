from __future__ import annotations
from fastapi import APIRouter, Path as FastApiPath
from fastapi.responses import FileResponse

from ..spec.openapi import OPENAPI_TAG_NAME
from ..spec.errors import HttpUnexpectedError_CodeShouldBeUnreachable
from ..routers_types.playlists import (
  PlaylistGetAll_Response200,
  PlaylistGetOne_Response200,
  PlaylistGetOne_ResponseError404,
  PlaylistAddOne_RequestBody,
  PlaylistAddOne_Response200,
  PlaylistAddOne_ResponseError404,
  PlaylistAddOne_ResponseError500,
  PlaylistEditPlaylist_RequestBody,
  PlaylistEditPlaylist_Response200,
  PlaylistEditPlaylist_ResponseError404,
  PlaylistEditPlaylist_ResponseError500,
  PlaylistSpotifyRefetchPlaylist_Response200,
  PlaylistSpotifyRefetchPlaylist_ResponseError404,
  PlaylistSpotifyRefetchPlaylist_ResponseError500,
  PlaylistEditTrack_RequestBody,
  PlaylistEditTrack_Response200,
  PlaylistEditTrack_ResponseError404,
  PlaylistEditTrack_ResponseError500,
  PlaylistYoutubeAutoSearchUrlSingleTrack_Response200,
  PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError404,
  PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500,
  PlaylistYoutubeAutoSearchUrlAllTracks_Response200,
  PlaylistYoutubeAutoSearchUrlAllTracks_ResponseError404,
  PlaylistDiskGetAudioFile_Response200,
  PlaylistDiskGetAudioFile_ResponseError404,
  PlaylistDiskDownloadSingleTrack_Response200,
  PlaylistDiskDownloadSingleTrack_ResponseError404,
  PlaylistDiskDownloadSingleTrack_ResponseError500,
  PlaylistDiskDownloadAllTracks_Response200,
  PlaylistDiskDownloadAllTracks_ResponseError404,
  PlaylistDiskDeleteTrackFile_Response200,
  PlaylistDiskDeleteTrackFile_ResponseError404,
)

from models.examples import EXAMPLE_TRACK_DERIVED,EXAMPLE_PLAYLIST_DERIVED

from core.singleton.logger import loggerHTTP as logger
from core.singleton.service_playlist import servicePlaylist

from core.classes.music_providers.utils_spotify import UtilsSpotify

# ============================================================================
# Playlists endpoints
# ============================================================================

router = APIRouter(
  prefix="/playlists", 
  tags=[OPENAPI_TAG_NAME.PLAYLIST],
)

@router.get("/", 
            operation_id="playlistGetAll", 
            summary="Get all playlists",
            description="Get all saved playlists (PlaylistRaw) from user config",
            )
async def playlists_getAll() -> PlaylistGetAll_Response200:
  logger.info("GET ALL PLAYLISTS")
  result = servicePlaylist.getPlaylistsRaw()
  playlistsRawItems = result[2]
  return playlistsRawItems

@router.get("/{playlist_id}", 
            operation_id="playlistGetOne", 
            summary="Get single playlist",
            description="Get single playlist (PlaylistDerived) from user config",
            responses={
              404: { "model": PlaylistGetOne_ResponseError404 },
            },
            )
async def playlist_getOne(
  playlist_id: str = FastApiPath(description="Spotify playlist id",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistGetOne_Response200:
  logger.info(f"GET ONE PLAYLIST, playlist_id={playlist_id}")
  result = await servicePlaylist.getPlaylistDerived(playlist_id=playlist_id)
  if result[0] == False:
    if result[1] == "DB_READ_ERROR":
      message = f"Playlist {playlist_id} not found in user config. Reason: {result[1]}"
      logger.error(message)
      raise PlaylistGetOne_ResponseError404(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  playlistDerived = result[2]
  return playlistDerived
  
@router.post("/add", 
             operation_id="playlistAddOne", 
             summary="Add new playlist",
             description="Add new playlist to user config by spotify playlist url",
             responses={
               404: { "model": PlaylistAddOne_ResponseError404 },
               500: { "model": PlaylistAddOne_ResponseError500 },
             }
             )
async def playlist_addOne(
  requestBody: PlaylistAddOne_RequestBody
) -> PlaylistAddOne_Response200:
  logger.info(f"ADD PLAYLIST, requestBody: {requestBody}")
  result = servicePlaylist.addPlaylist(payload=requestBody)
  if result[0] == False:
    if result[1] == "SPOTIFY_FETCH_ERROR":
      spotifyPlaylistId = UtilsSpotify.deriveSpotifyPlaylistIdFromUrl(spotifyPlaylistUrl=requestBody.playlistSpotifyUrl)
      message = f"Playlist {spotifyPlaylistId} not found in Spotify. Maybe you made the playlist private or deleted it from Spotify?"
      logger.error(message)
      raise PlaylistAddOne_ResponseError404(message=message).toHttpException()
    if result[1] == "DB_ADD_ERROR":
      message = f"Error adding playlist to user config: {result[2]}"
      logger.error(message)
      raise PlaylistAddOne_ResponseError500(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True

@router.post("/edit-playlist", 
             operation_id="playlistEditPlaylist", 
             summary="Edit playlist",
             description="Edit playlist in user config (directory name, ...)",
             responses={
               404: { "model": PlaylistEditPlaylist_ResponseError404 },
               500: { "model": PlaylistEditPlaylist_ResponseError500 },
             },
             )
async def playlist_editOne(
  requestBody: PlaylistEditPlaylist_RequestBody
) -> PlaylistEditPlaylist_Response200:
  logger.info(f"EDIT ONE PLAYLIST, requestBody: {requestBody}")
  result = servicePlaylist.updatePlaylist(payload=requestBody)
  if result[0] == False:
    if result[1] == "NOT_FOUND":
      message = f"Playlist not found {requestBody.playlist_id}"
      logger.error(message)
      raise PlaylistEditPlaylist_ResponseError404(message=message).toHttpException()
    if result[1] == "DB_READ_ERROR":
      message = f"Db read error {requestBody.playlist_id}"
      logger.error(message)
      raise PlaylistEditPlaylist_ResponseError500(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True
    
@router.post("/{playlist_id}/spotify/refetch", 
             operation_id="playlistSpotifyRefetchPlaylist", 
             summary="Refetch playlist Spotify side",
             description="Refetch playlist Spotify side and save to user config",
             responses={
              404: { "model": PlaylistSpotifyRefetchPlaylist_ResponseError404 },
              500: { "model": PlaylistSpotifyRefetchPlaylist_ResponseError500 },
             },
             )
async def playlist_spotify_refetchPlaylist(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistSpotifyRefetchPlaylist_Response200:
  logger.info(f"REFETCH PLAYLIST SPOTIFY SIDE, playlist_id {playlist_id}")
  result = await servicePlaylist.spotify_refetchPlaylist_then_updatePlaylist(playlist_id=playlist_id)
  if result[0] == False:
    if result[1] == "PLAYLIST_NOT_FOUND_IN_DB":
      message = f"Playlist {playlist_id} not found in your config"
      logger.error(message)
      raise PlaylistSpotifyRefetchPlaylist_ResponseError404(message=message).toHttpException()
    if result[1] == "SPOTIFY_FETCH_ERROR":
      message = f"Error refetching playlist {playlist_id} from Spotify. Maybe you made the playlist private or deleted it from Spotify?"
      logger.error(message)
      raise PlaylistSpotifyRefetchPlaylist_ResponseError404(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True

@router.post("/edit-track", 
             operation_id="playlistEditTrack", 
             summary="Edit playlist track",
             description="Edit playlist track in user config (youtube url, ...)",
             responses={
               404: { "model": PlaylistEditTrack_ResponseError404 },
               500: { "model": PlaylistEditTrack_ResponseError500 },
             },
             )
async def playlist_editTrack(requestBody: PlaylistEditTrack_RequestBody) -> PlaylistEditTrack_Response200:
  logger.info(f"EDIT PLAYLIST TRACK, requestBody={requestBody}")
  result = servicePlaylist.updatePlaylistTrack(payload=requestBody)
  if result[0] == False:
    if result[1] == "TRACK_NOT_FOUND_IN_DB":
      message = f"Track not found in playlist, playlist_id={requestBody.playlist_id}, track_id={requestBody.track_id}"
      logger.error(message)
      raise PlaylistEditTrack_ResponseError404(message=message).toHttpException()
    if result[1] == "DB_UPDATE_TRACK_ERROR":
      message = f"Error updating playlist track, playlist_id={requestBody.playlist_id}, track_id={requestBody.track_id}"
      logger.error(message)
      raise PlaylistEditTrack_ResponseError500(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True
    
@router.post("/{playlist_id}/track/{track_id}/youtube/auto-search-url", 
             operation_id="playlistYoutubeAutoSearchUrlSingleTrack", 
             summary="Auto-Search YouTube URL for a track",
             description="Auto find-and-set YouTube URL for a playlist track, using track name and artist as search query",
             responses={
               404: { "model": PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError404 },
               500: { "model": PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500 },
             },
             )
async def playlist_youtube_autoSearchUrl_singleTrack(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistYoutubeAutoSearchUrlSingleTrack_Response200:
  logger.info(f"YOUTUBE AUTO-SEARCH URL SINGLE TRACK, playlist_id: {playlist_id}, track_id: {track_id}")
  result = servicePlaylist.youtube_autoSearchUrlSingleTrack_then_updateTrack(playlist_id=playlist_id, track_id=track_id)
  if result[0] == False:
    if result[1] == "TRACK_NOT_FOUND_IN_DB":
      message = f"Track {track_id} not found in playlist {playlist_id}"
      logger.error(message)
      raise PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError404(message=message).toHttpException()
    if result[1] == "YOUTUBE_URL_NOT_FOUND":
      message = f"Could not find YouTube URL for track {track_id}"
      logger.error(message)
      raise PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500(message=message).toHttpException()
    if result[1] == "DB_UPDATE_TRACK_ERROR":
      message = f"Error updating track {track_id} in playlist {playlist_id}"
      logger.error(message)
      raise PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True
  
@router.post("/{playlist_id}/youtube/auto-search-url", 
             operation_id="playlistYoutubeAutoSearchUrlAllTracks", 
             summary="Auto-Search YouTube URL for all tracks (Async Job)",
             description="Auto find-and-set YouTube URL for all playlist tracks that have no YouTube URL",
             responses={
               404: { "model": PlaylistYoutubeAutoSearchUrlAllTracks_ResponseError404 },
             },
             )
async def playlist_youtube_autoSearchUrl_allTracks(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistYoutubeAutoSearchUrlAllTracks_Response200:
  logger.info(f"Find YouTube URL for all tracks of playlist {playlist_id}")
  result = await servicePlaylist.youtube_autoSearchUrlAllTracks_scheduleJob(playlist_id=playlist_id)
  if result[0] == False:
    if result[1] == "PLAYLIST_NOT_FOUND_IN_DB":
      message = f"Playlist {playlist_id} not found in your config"
      logger.error(message)
      raise PlaylistYoutubeAutoSearchUrlAllTracks_ResponseError404(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True

@router.get("/{playlist_id}/track/{track_id}/disk/get-audio-file", 
            operation_id="playlistDiskGetAudioFile", 
            summary="Get Audio File of track",
            description="Return Playlist track disk file (downloaded) as Binary File. Use this to play the track in <audio src> tag",
            responses={
              404: { "model": PlaylistDiskGetAudioFile_ResponseError404 },
            }
            )
async def playlist_disk_getAudioFile(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistDiskGetAudioFile_Response200:
  logger.info(f"DISK GET AUDIO FILE, playlist_id: {playlist_id}, track_id: {track_id}")
  result = servicePlaylist.disk_getTrackFileAsBinary(playlist_id=playlist_id, track_id=track_id)
  if result[0] == False:
    if result[1] == "TRACK_NOT_FOUND_IN_DB":
      message = f"Track {track_id} not found in playlist {playlist_id}"
      logger.error(message)
      raise PlaylistDiskGetAudioFile_ResponseError404(message=message).toHttpException()
    if result[1] == "FILE_NOT_FOUND_ON_DISK":
      message = f"File for track {track_id} not found on disk"
      logger.error(message)
      raise PlaylistDiskGetAudioFile_ResponseError404(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  filePath = result[2]
  return FileResponse(
    path=filePath,
    media_type="audio/mpeg",
    filename="song.mp3",
  )
    
@router.post("/{playlist_id}/track/{track_id}/disk/download", 
             operation_id="playlistDiskDownloadSingleTrack", 
             summary="Download (YouTube -> MP3) for a track",
             description="Download single playlist track from YouTube as MP3 and save to disk",
             responses={
               404: { "model": PlaylistDiskDownloadSingleTrack_ResponseError404 },
               500: { "model": PlaylistDiskDownloadSingleTrack_ResponseError500 },
             },
             )
async def playlist_disk_download_singleTrack(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistDiskDownloadSingleTrack_Response200:
  logger.info(f"DISK DOWNLOAD SINGLE TRACK, playlist_id: {playlist_id}, track_id:")
  result = await servicePlaylist.disk_downloadSingleTrack(playlist_id=playlist_id, track_id=track_id)
  if result[0] == False:
    if result[1] == "TRACK_NOT_FOUND_IN_DB":
      message = f"Track {track_id} not found in playlist {playlist_id}"
      logger.error(message)
      raise PlaylistDiskDownloadSingleTrack_ResponseError404(message=message).toHttpException()
    if result[1] == "ERROR_DOWNLOADING":
      message = f"Error downloading track {track_id} from YouTube. Reason: {result[2]}"
      logger.error(message)
      raise PlaylistDiskDownloadSingleTrack_ResponseError500(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True
  
@router.post("/{playlist_id}/disk/download-all/job/start", 
             operation_id="playlistDiskDownloadAllTracks", 
             summary="Download (YouTube -> MP3) for all tracks (Async Job)",
             description="Start async job. Download track from YouTube as MP3 and save to disk, for all tracks of the playlist that have YouTube URL and are not downloaded yet",
             responses={
               404: { "model": PlaylistDiskDownloadAllTracks_ResponseError404 },
             },
             )
async def playlist_disk_download_allTracks(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistDiskDownloadAllTracks_Response200:
  logger.info(f"DISK DOWNLOAD ALL TRACKS, playlist_id: {playlist_id}")
  result = await servicePlaylist.disk_downloadAllTracks(playlist_id=playlist_id)
  if result[0] == False:
    if result[1] == "PLAYLIST_NOT_FOUND_IN_DB":
      message = f"Playlist {playlist_id} not found in your config"
      logger.error(message)
      raise PlaylistDiskDownloadAllTracks_ResponseError404(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True
  
@router.post("/{playlist_id}/track/{track_id}/disk/delete-file", 
             operation_id="playlistDiskDeleteTrackFile", 
             summary="Delete playlist track file",
             description="Delete playlist track file (downloaded) from disk",
             responses={
               404: { "model": PlaylistDiskDeleteTrackFile_ResponseError404 },
             },
             )
async def playlist_disk_deleteTrackFile(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistDiskDeleteTrackFile_Response200:
  logger.info(f"DISK DELETE TRACK FILE, playlist_id: {playlist_id}, track_id: {track_id}")
  result = servicePlaylist.disk_deleteTrackFile(playlist_id=playlist_id, track_id=track_id)
  if result[0] == False:
    if result[1] == "TRACK_NOT_FOUND_IN_DB":
      message = f"Track {track_id} not found in playlist {playlist_id}"
      logger.error(message)
      raise PlaylistDiskDeleteTrackFile_ResponseError404(message=message).toHttpException()
    if result[1] == "FILE_NOT_FOUND":
      message = f"Track audio file for track {track_id} not found, playlist {playlist_id}"
      logger.error(message)
      raise PlaylistDiskDeleteTrackFile_ResponseError404(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True
  