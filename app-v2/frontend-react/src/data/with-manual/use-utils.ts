import { useMutation } from "@tanstack/react-query";
import { apiClientManual as apiClient } from '#/lib/api-client/client-manual/client.singleton';
import { type InferCallOptions } from '#/lib/api-client/client-manual/lib/types.http';

const queryKeys = {
  mutation: {
    diskRevealInFinder: ['utils', 'mutation', 'diskRevealInFinder']
  }
};

export function useMutationUtilsDiskRevealInFinder() {
  return useMutation({
    mutationKey: queryKeys.mutation.diskRevealInFinder,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.utilsDiskRevealInFinder>
    ) => {
      return apiClient.apiHttp
        .utilsDiskRevealInFinder(payload);
    }
  });
}