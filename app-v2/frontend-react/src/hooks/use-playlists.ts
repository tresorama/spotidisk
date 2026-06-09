import { useQuery } from '@tanstack/react-query';
import { apiClient } from '#/lib/api-client/client';
import type { DerivedPlaylist } from '#/lib/api-client/types';

export function usePlaylists() {
  return useQuery({
    queryKey: ['playlists'],
    queryFn: () => apiClient.getPlaylists(),
  });
}

export function usePlaylist(playlistId: DerivedPlaylist['spotify_id']) {
  return useQuery({
    queryKey: ['playlists', playlistId],
    queryFn: () => apiClient.getPlaylist(playlistId),
  });
}
