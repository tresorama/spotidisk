import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClientKubbSdk as apiClient } from '#/lib/api-client/client-kubb-sdk/client.singleton';
import { type OperationsTypes } from './types';


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
      return apiClient.apiHttp.api
        .settingsGetSettings()
        .then(res => res.data);
    }
  });
};

export function useMutationUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: queryKeys.mutation.updateSettings,
    mutationFn: async (
      payload: OperationsTypes.SettingsUpdateSettingsOptions,
    ) => {
      return apiClient.apiHttp.api
        .settingsUpdateSettings(payload)
        .then(res => res.data);
    },
    onSettled: () => {
      queryClient.invalidateQueries();
    }
  });
}