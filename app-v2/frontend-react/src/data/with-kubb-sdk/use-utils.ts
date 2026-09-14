import { useMutation } from "@tanstack/react-query";
import { apiClientKubbSdk as apiClient } from '#/lib/api-client/client-kubb-sdk/client.singleton';
import { type OperationsTypes } from './types';
import { toast } from "@/components/ui/sonner";

const queryKeys = {
  mutation: {
    diskRevealInFinder: ['utils', 'mutation', 'diskRevealInFinder']
  }
};

export function useMutationUtilsDiskRevealInFinder() {
  return useMutation({
    mutationKey: queryKeys.mutation.diskRevealInFinder,
    mutationFn: async (
      payload: OperationsTypes.UtilsDiskRevealInFinderOptions
    ) => {
      return apiClient.apiHttp.api
        .utilsDiskRevealInFinder(payload)
        .then(res => res.data)
        .then(data => {
          toast.success('Disk folder revealed');
          return data;
        });
    }
  });
}