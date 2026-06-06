import { useQuery } from '@tanstack/react-query';
import { apiClient } from '#/lib/api-client/client';

export function usePlaylists() {
  return useQuery({
    queryKey: ['playlists'],
    queryFn: () => apiClient.getPlaylists(),
  });
}
