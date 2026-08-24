import { useMutation } from '@tanstack/react-query';
import { apiClientManual as apiClient } from '#/lib/api-client/client-manual/client.singleton';

const queryKeys = {
  mutation: {
    jobDemoStart: ['playlists', 'mutation', 'demo', 'job', 'start'],
  },
};

export function useMutationDemoJobDemoStart() {
  return useMutation({
    mutationKey: queryKeys.mutation.jobDemoStart,
    mutationFn: async () => apiClient.apiHttp.demoJobDemoStart(),
  });
}

