import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClientKubbSdk as apiClient } from '#/lib/api-client/client-kubb-sdk/client.singleton';
import { type OperationsTypes } from './types';
import { toast } from '#/components/ui/sonner';

const queryKeys = {
  query: {
    playlistList: ['playlists'],
    playlistDetails: (playlistId: string) => ['playlists', playlistId],
  },
  mutation: {
    addPlaylist: ['playlists', 'mutation', 'add'],
    deletePlaylist: ['playlists', 'mutation', 'delete'],
    updatePlaylist: ['playlists', 'mutation', 'update'],
    spotifyRefetchPlaylist: ['playlists', 'mutation', 'spotify', 'refetch'],
    updateTrack: ['playlists', 'mutation', 'update-track'],
    youtubeAutoSearchUrlSingleTrack: ['playlists', 'mutation', 'youtube', 'auto-search-url-single-track'],
    youtubeAutoSearchUrlAllTracks: ['playlists', 'mutation', 'youtube', 'auto-search-url-all-tracks'],
    diskDeleteTrack: ['playlists', 'mutation', 'disk', 'delete-file'],
    diskDownloadSingleTrack: ['playlists', 'mutation', 'disk', 'download-single-track'],
    diskDownloadAllTracks: ['playlists', 'mutation', 'disk', 'download-all-tracks'],
    diskDeleteOrphanTracks: ['playlists', 'mutation', 'disk', 'delete-orphan-tracks'],
  },
};


/** Get all playlist items */
export function usePlaylists() {
  return useQuery({
    queryKey: queryKeys.query.playlistList,
    queryFn: async () => {
      return apiClient.apiHttp.api
        .playlistGetAll()
        .then(res => res.data)
        .then(unsortedItems => {
          return {
            unsortedItems,
            sortedItems: [...unsortedItems].sort((a, b) => a.name.localeCompare(b.name)),
          };
        });
    }
  });
}

/** Get a single playlist data */
export function usePlaylist(payload: OperationsTypes.PlaylistGetOneOptions) {
  return useQuery({
    queryKey: queryKeys.query.playlistDetails(payload.path.playlist_id),
    queryFn: async () => {
      return apiClient.apiHttp.api
        .playlistGetOne(payload)
        .then(res => res.data);
    }
  });
}

export function useAddPlaylist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updateTrack,
    mutationFn: async (
      payload: OperationsTypes.PlaylistAddOneOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistAddOne(payload)
        .then(res => res.data);
    },
    onSettled: () => {
      [
        queryKeys.query.playlistList
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Delete playlist */
export function useMutationPlaylistDeletePlaylist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.deletePlaylist,
    mutationFn: async (
      payload: OperationsTypes.PlaylistDeleteOneOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistDeleteOne(payload)
        .then(res => res.data)
        .then(data => {
          toast.success('Playlist deleted');
          return data;
        });
    },
    onSettled: (_data, _error, payload) => {
      [
        queryKeys.query.playlistList,
        queryKeys.query.playlistDetails(payload.path.playlist_id),
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Update playlist details */
export function useMutationPlaylistUpdatePlaylist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updatePlaylist,
    mutationFn: async (
      payload: OperationsTypes.PlaylistEditPlaylistOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistEditPlaylist(payload)
        .then(res => res.data)
        .then(data => {
          toast.success('Playlist updated');
          return data;
        });
    },
    onSettled: (_data, _error, payload) => {
      [
        queryKeys.query.playlistList,
        queryKeys.query.playlistDetails(payload.body.playlist_id),
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}

/** Refetch "spotify" playlist data, and update persisted data */
export function useMutationPlaylistRefetchSpotifySide() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.spotifyRefetchPlaylist,
    mutationFn: async (
      payload: OperationsTypes.PlaylistSpotifyRefetchPlaylistOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistSpotifyRefetchPlaylist(payload)
        .then(res => res.data);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.path.playlist_id),
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
      payload: OperationsTypes.PlaylistEditTrackOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistEditTrack(payload)
        .then(res => res.data);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.body.playlist_id),
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
    mutationFn: async (
      payload: OperationsTypes.PlaylistYoutubeAutoSearchUrlSingleTrackOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistYoutubeAutoSearchUrlSingleTrack(payload)
        .then(res => res.data);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.path.playlist_id)
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
      payload: OperationsTypes.PlaylistYoutubeAutoSearchUrlAllTracksOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistYoutubeAutoSearchUrlAllTracks(payload)
        .then(res => res.data);
    },
  });
}

/** Delete a track from disk and update persisted data */
export function useMutationPlaylistDeleteTrackFromDisk() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.diskDeleteTrack,
    mutationFn: async (
      payload: OperationsTypes.PlaylistDiskDeleteTrackFileOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistDiskDeleteTrackFile(payload)
        .then(res => res.data);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.path.playlist_id)
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
      payload: OperationsTypes.PlaylistDiskDownloadSingleTrackOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistDiskDownloadSingleTrack(payload)
        .then(res => res.data);
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.path.playlist_id)
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
      payload: OperationsTypes.PlaylistDiskDownloadAllTracksOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistDiskDownloadAllTracks(payload)
        .then(res => res.data);
    },
  });
}

/** Delete orphan tracks from disk */
export function useMutationPlaylistDeleteOrphanTracks() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.diskDeleteOrphanTracks,
    mutationFn: async (
      payload: OperationsTypes.PlaylistDiskDeleteOrphanTracksOptions
    ) => {
      return apiClient.apiHttp.api
        .playlistDiskDeleteOrphanTracks(payload)
        .then(res => res.data)
        .then(data => {
          toast.success('Orphan tracks deleted');
          return data;
        });
    },
    onSettled: (_responseData, _error, mutationInput) => {
      [
        queryKeys.query.playlistDetails(mutationInput.path.playlist_id)
      ]
        .forEach(queryKey => queryClient.invalidateQueries({ queryKey }));
    }
  });
}