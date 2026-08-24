import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClientManual as apiClient } from '#/lib/api-client/client-manual/client.singleton';
import { type InferCallOptions } from '#/lib/api-client/client-manual/lib/types.http';


const queryKeys = {
  query: {
    playlistList: ['playlists'],
    playlistDetails: (playlistId: string) => ['playlists', playlistId],
  },
  mutation: {
    addPlaylist: ['playlists', 'mutation', 'add'],
    spotifyRefetchPlaylist: ['playlists', 'mutation', 'spotify', 'refetch'],
    updateTrack: ['playlists', 'mutation', 'update-track'],
    youtubeAutoSearchUrlSingleTrack: ['playlists', 'mutation', 'youtube', 'auto-search-url-single-track'],
    youtubeAutoSearchUrlAllTracks: ['playlists', 'mutation', 'youtube', 'auto-search-url-all-tracks'],
    diskDeleteTrack: ['playlists', 'mutation', 'disk', 'delete-file'],
    diskDownloadSingleTrack: ['playlists', 'mutation', 'disk', 'download-single-track'],
    diskDownloadAllTracks: ['playlists', 'mutation', 'disk', 'download-all-tracks'],
  },
};

export function useAddPlaylist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updateTrack,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistAddOne>
    ) => {
      return apiClient.apiHttp
        .playlistAddOne(payload);
    },
    onSettled: () => {
      [
        queryKeys.query.playlistList
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Get all playlist items */
export function usePlaylists() {
  return useQuery({
    queryKey: queryKeys.query.playlistList,
    queryFn: async () => {
      return apiClient.apiHttp
        .playlistGetAll()
        .then(allItems => {
          const sortedItems = [...allItems].sort((a, b) => a.name.localeCompare(b.name));
          return {
            originalSortedItems: allItems,
            sortedItems,
          };
        });
    }
  });
}

/** Get a single playlist data */
export function usePlaylist(payload: InferCallOptions<typeof apiClient.apiHttp.playlistGetOne>) {
  return useQuery({
    queryKey: queryKeys.query.playlistDetails(payload.playlistId),
    queryFn: async () => {
      return apiClient.apiHttp
        .playlistGetOne(payload);
    }
  });
}

/** Refetch "spotify" playlist data, and update persisted data */
export function useMutationPlaylistRefetchSpotifySide() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.spotifyRefetchPlaylist,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistSpotifyRefetch>
    ) => {
      return apiClient.apiHttp
        .playlistSpotifyRefetch(payload);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.playlistId),
        queryKeys.query.playlistList
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Update a track of a playlist, and update persisted data */
export function useMutationPlaylistUpdateTrack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updateTrack,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistEditTrack>
    ) => {
      return apiClient.apiHttp
        .playlistEditTrack(payload);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.playlist_id),
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Find a track youtube url on youtube and update persisted data */
export function useMutationPlaylistFindTrackYoutubeUrlSingleTrack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.youtubeAutoSearchUrlSingleTrack,
    mutationFn: (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistYoutubeAutoSearchUrlSingleTrack>
    ) => {
      return apiClient.apiHttp
        .playlistYoutubeAutoSearchUrlSingleTrack(payload);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.playlistId)
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Find Youtube urls for all tracks of a playlist (only if missing) and update persisted data */
export function useMutationPlaylistFindTrackYoutubeUrlAllTracks() {
  return useMutation({
    mutationKey: queryKeys.mutation.youtubeAutoSearchUrlAllTracks,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistYoutubeAutoSearchUrlAllTracks>
    ) => {
      return apiClient.apiHttp
        .playlistYoutubeAutoSearchUrlAllTracks(payload);
    }
  });
}


/** Delete a track from disk and update persisted data */
export function useMutationPlaylistDeleteTrackFromDisk() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.diskDeleteTrack,
    mutationFn: (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistDiskDeleteFile>
    ) => {
      return apiClient.apiHttp
        .playlistDiskDeleteFile(payload);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.playlistId)
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Download a track from youtube and update persisted data */
export function useMutationPlaylistDownloadSingleTrack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.diskDownloadSingleTrack,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistDiskDownloadSingleTrack>
    ) => {
      return apiClient.apiHttp
        .playlistDiskDownloadSingleTrack(payload);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.playlistId)
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Download all (missing) tracks from youtube and update persisted data */
export function useMutationPlaylistDownloadAllTracks() {
  return useMutation({
    mutationKey: queryKeys.mutation.diskDownloadAllTracks,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.playlistDiskDownloadAllTracks>
    ) => {
      return apiClient.apiHttp
        .playlistDiskDownloadAllTracks(payload);
    }
  });
}
