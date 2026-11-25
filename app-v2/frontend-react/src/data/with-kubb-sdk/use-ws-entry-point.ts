import { useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { apiClientKubbSdk as apiClient } from '#/lib/api-client/client-kubb-sdk/client.singleton';

import { useGlobalWebSocketConnectionActions } from "#/state/global.ws";
import { useGlobalEventsLogsActions } from "#/state/global.backend-events";
import { useGlobalJobProgressActions } from "#/state/global.job-progress";

import { useWebSocketConnection } from "#/utils/hooks/use-web-socket";
import { toast, type ToastId } from "#/components/ui/sonner";
import { toastThrottled } from "#/components/ui/sonner.throttled";

export function useWsEntryPoint() {

  const queryClient = useQueryClient();
  const wsActions = useGlobalWebSocketConnectionActions();
  const eventsLogsActions = useGlobalEventsLogsActions();
  const jobProgressActions = useGlobalJobProgressActions();

  const refToastConnectingId = useRef<ToastId | null>(null);

  useWebSocketConnection({
    initWsConnection: () => apiClient.apiWs.wsEntryPointConnect().getWs(),
    onConnectionStateChange: (data) => {
      if (data.status === 'connecting') {
        wsActions.setStatus("connecting");
        eventsLogsActions.addEvent({ data: ['useWsEntryPoint', 'Connecting to backend'] });
        refToastConnectingId.current = toast.loading('Connecting to backend');
        return;
      }

      if (data.status === 'connected') {
        wsActions.setStatus("connected");
        eventsLogsActions.addEvent({ data: ['useWsEntryPoint', 'Connected to backend'] });
        toast.success('Connected to backend', { id: refToastConnectingId.current ?? undefined });
        return;
      }

      if (data.status === 'disconnected') {
        wsActions.setStatus("disconnected");
        eventsLogsActions.addEvent({ data: ['useWsEntryPoint ', 'Disconnected from backend'] });
        toast.error('Disconnected from backend', { id: refToastConnectingId.current ?? undefined });
        return;
      }

      throw new Error(`Unknown ws connection status: ${data}`);
    },
    onMessageFromBackend: (event) => {
      try {
        // parse ws message
        const schema = apiClient.apiWs.wsEntryPointConnect()._responseDataSchema;
        const backendEvent = schema.parse(JSON.parse(event.data));

        // append it to logs actions
        eventsLogsActions.addEvent({
          receivedAt: new Date().toISOString(),
          data: backendEvent
        });

        // based on event type do something
        switch (backendEvent.payload.kind) {
          case "MESSAGE":
            // we use `toastThrottled` intead of `toast` because websocket messages can be triggred a lot of time
            // in a short amount of time, leading to memory problm that causes the browser tab to freeeze
            if (backendEvent.payload.severity === "INFO") toastThrottled.message(backendEvent.payload.text);
            else if (backendEvent.payload.severity === "WARNING") toastThrottled.warning(backendEvent.payload.text);
            else if (backendEvent.payload.severity === "ERROR") toastThrottled.error(backendEvent.payload.text);
            else if (backendEvent.payload.severity === "SUCCESS") toastThrottled.success(backendEvent.payload.text);
            break;
          case "FRONTEND_QUERY_INVALIDATION":
            queryClient.invalidateQueries({ queryKey: backendEvent.payload.queryKeys });
            break;
          case "JOB_PROGRESS":
            jobProgressActions.setJobProgress(backendEvent.payload);
            break;
          default:
            break;
        }
      } catch (error) {
        eventsLogsActions.addEvent({ data: [/*`useWsEntryPoint`, `🏠 BE`, */`ERROR: parsing ws message`, event, error] });
        console.log([`useWsEntryPoint`, `ERROR: parsing ws message`, event, error]);
        toast.error(`Error processing server message!`);
      }
    }
  });
}