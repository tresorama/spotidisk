import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '#/lib/api-client/client';
import { useWebSocket } from '@/hooks/use-web-socket';

const queryKeys = {
  query: {
    playlistList: ['playlists'],
    playlistDetails: (playlistId: string) => ['playlists', playlistId],
  },
  mutation: {
    spotifyRefetchPlaylist: ['playlists', 'mutation', 'spotify', 'refetch'],
    updateTrack: ['playlists', 'mutation', 'update-track'],
    youtubeAutoSearchUrl: ['playlists', 'mutation', 'youtube', 'auto-search-url'],
    diskDownloadTrack: ['playlists', 'mutation', 'disk', 'download'],
    diskDeleteTrack: ['playlists', 'mutation', 'disk', 'delete-file'],
    diskRevealInFinder: ['playlists', 'mutation', 'disk', 'reveal-in-finder'],
  }
};

/** Get all playlist items */
export function usePlaylists() {
  return useQuery({
    queryKey: queryKeys.query.playlistList,
    queryFn: () => apiClient.playlist_getAll(),
  });
}

/** Get a single playlist data */
export function usePlaylist(payload: Parameters<typeof apiClient.playlist_getOne>[0]) {
  return useQuery({
    queryKey: queryKeys.query.playlistDetails(payload.playlistId),
    queryFn: () => apiClient.playlist_getOne(payload),
  });
}

/** Refetch "spotify" playlist data, and update persisted data */
export function useMutationPlaylistRefetchSpotifySide() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.spotifyRefetchPlaylist,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_spotify_refetch>[0]
    ) => apiClient.playlist_spotify_refetch(payload),
    onSettled: (_responseData, _error, mutationInput) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.query.playlistDetails(mutationInput.playlistId)
      });
    }
  });
}

/** Update a track of a playlist, and update persisted data */
export function useMutationPlaylistUpdateTrack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updateTrack,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_updateTrack>[0]
    ) => apiClient.playlist_updateTrack(payload),
    onSettled: (_responseData, _error, mutationInput) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.query.playlistDetails(mutationInput.playlist_id)
      });
    }
  });
}

/** Find a track youtube url on youtube and update persisted data */
export function useMutationPlaylistFindTrackYoutubeUrl() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.youtubeAutoSearchUrl,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_youtube_autoSearchUrl>[0]
    ) => apiClient.playlist_youtube_autoSearchUrl(payload),
    onSettled: (_responseData, _error, mutationInput) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.query.playlistDetails(mutationInput.playlistId)
      });
    }
  });
}

/** Delete a track from disk and update persisted data */
export function useMutationPlaylistDeleteTrackFromDisk() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.diskDeleteTrack,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_disk_deleteFile>[0]
    ) => apiClient.playlist_disk_deleteFile(payload),
    onSettled: (_responseData, _error, mutationInput) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.query.playlistDetails(mutationInput.playlistId)
      });
    }
  });
}

/** Download a track from youtube and update persisted data */
export function useMutationPlaylistDownloadSingleTrackFromYoutubeToDisk() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.diskDownloadTrack,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_disk_download>[0]
    ) => apiClient.playlist_disk_download(payload),
    onSettled: (_responseData, _error, mutationInput) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.query.playlistDetails(mutationInput.playlistId)
      });
    }
  });
}

/** Reveal playlist's directory on disk using th OS "reveal" feature */
export function useMutationPlaylistDiskRevealInFinder() {
  return useMutation({
    mutationKey: queryKeys.mutation.diskRevealInFinder,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_disk_revealInFinder>[0]
    ) => apiClient.playlist_disk_revealInFinder(payload),
  });
}

export function useJobGetProgressWS() {
  type ResponseData = ReturnType<typeof apiClient.jobGetStatus>['responseDataType'];
  return useWebSocket<ResponseData>({
    initWsConnection: () => apiClient.jobGetStatus().ws,
  });
}