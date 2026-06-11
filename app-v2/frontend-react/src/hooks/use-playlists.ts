import { useQuery } from '@tanstack/react-query';
import { apiClient } from '#/lib/api-client/client';

export function usePlaylists() {
  return useQuery({
    queryKey: ['playlists'],
    queryFn: () => apiClient.getPlaylists(),
  });
}

export function usePlaylist(payload: Parameters<typeof apiClient.getPlaylist>[0]) {
  return useQuery({
    queryKey: ['playlists', payload],
    queryFn: () => apiClient.getPlaylist(payload),
  });
}
