import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '#/lib/api-client/client.singleton';

const queryKeys = {
  query: {
    playlistList: ['playlists'],
    playlistDetails: (playlistId: string) => ['playlists', playlistId],
  },
  mutation: {
    spotifyRefetchPlaylist: ['playlists', 'mutation', 'spotify', 'refetch'],
    updateTrack: ['playlists', 'mutation', 'update-track'],
    youtubeAutoSearchUrlSingleTrack: ['playlists', 'mutation', 'youtube', 'auto-search-url-single-track'],
    youtubeAutoSearchUrlAllTracks: ['playlists', 'mutation', 'youtube', 'auto-search-url-all-tracks'],
    diskRevealInFinder: ['playlists', 'mutation', 'disk', 'reveal-in-finder'],
    diskDeleteTrack: ['playlists', 'mutation', 'disk', 'delete-file'],
    diskDownloadSingleTrack: ['playlists', 'mutation', 'disk', 'download-single-track'],
    diskDownloadAllMissingTracks: ['playlists', 'mutation', 'disk', 'download-all-missing-tracks'],
  },
  demo: {
    jobDemoStart: ['playlists', 'mutation', 'demo', 'job', 'start'],
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
export function useMutationPlaylistFindTrackYoutubeUrlSingleTrack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.youtubeAutoSearchUrlSingleTrack,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_youtube_autoSearchUrlSingleTrack>[0]
    ) => apiClient.playlist_youtube_autoSearchUrlSingleTrack(payload),
    onSettled: (_responseData, _error, mutationInput) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.query.playlistDetails(mutationInput.playlistId)
      });
    }
  });
}

/** Find Youtube urls for all tracks of a playlist (only if missing) and update persisted data */
export function useMutationPlaylistFindTrackYoutubeUrlAllTracks() {
  return useMutation({
    mutationKey: queryKeys.mutation.youtubeAutoSearchUrlAllTracks,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_youtube_autoSearchUrlAllTracks>[0]
    ) => apiClient.playlist_youtube_autoSearchUrlAllTracks(payload),
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
    mutationKey: queryKeys.mutation.diskDownloadSingleTrack,
    mutationFn: (
      payload: Parameters<typeof apiClient.playlist_disk_downloadSingleTrack>[0]
    ) => apiClient.playlist_disk_downloadSingleTrack(payload),
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

export function useMutationJobDemoStart() {
  return useMutation({
    mutationKey: queryKeys.demo.jobDemoStart,
    mutationFn: () => apiClient.job_jobDemo_start(),
  });
}

export function useMutationPlaylistDownloadAllMissingTracks() {
  return useMutation({
    mutationKey: queryKeys.mutation.diskDownloadAllMissingTracks,
    mutationFn: (
      payload: Parameters<typeof apiClient.job_jobPlaylistDownloadAllMissingTracks_start>[0]
    ) => apiClient.job_jobPlaylistDownloadAllMissingTracks_start(payload),
  });
}
