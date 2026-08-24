import { useMutation } from '@tanstack/react-query';

import { apiClientKubbSdk as apiClient } from '@/lib/api-client/client-kubb-sdk/client.singleton';

const queryKeys = {
  mutation: {
    jobDemoStart: ['playlists', 'mutation', 'demo', 'job', 'start'],
  },
};

export function useMutationDemoJobDemoStart() {
  return useMutation({
    mutationKey: queryKeys.mutation.jobDemoStart,
    mutationFn: async () => {
      return apiClient.apiHttp.api
        .demoJobDemoStart()
        .then(res => res.data);
    }
  });
}

