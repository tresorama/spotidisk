import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClientManual as apiClient } from '#/lib/api-client/client-manual/client.singleton';
import { type InferCallOptions } from '#/lib/api-client/client-manual/lib/types.http';

const queryKeys = {
  query: {
    settings: ['settings']
  },
  mutation: {
    updateSettings: ['settings', 'mutation', 'updateSettings']
  }
};

export const useSettings = () => {
  return useQuery({
    queryKey: queryKeys.query.settings,
    queryFn: async () => {
      return apiClient.apiHttp
        .settingsGetSettings();
    }
  });
};

export function useMutationUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updateSettings,
    mutationFn: async (
      payload: InferCallOptions<typeof apiClient.apiHttp.settingsUpdateSettings>
    ) => {
      return apiClient.apiHttp
        .settingsUpdateSettings(payload);
    },
    onSettled: () => {
      queryClient.invalidateQueries();
    }
  });
}