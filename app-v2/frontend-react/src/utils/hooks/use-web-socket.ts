import { useEffect } from "react";

export function useWebSocketConnection({
  initWsConnection,
  onConnectionStateChange,
  onMessageFromBackend,
}: {
  initWsConnection: () => WebSocket;
  onConnectionStateChange?: (data: (
    | { status: "connecting", ws: null; }
    | { status: "connected", ws: WebSocket; event: Event; }
    | { status: "disconnected", ws: WebSocket; event: CloseEvent; }
  )) => void;
  onMessageFromBackend?: (event: MessageEvent<any>) => void;
}) {

  useEffect(
    () => {
      onConnectionStateChange?.({ status: "connecting", ws: null });

      // connect (send request to backend)
      const ws = initWsConnection();

      // add event listeners
      const handlers = {
        onOpen: (event: Event) => {
          onConnectionStateChange?.({ status: "connected", ws, event });
        },
        onClose: (event: CloseEvent) => {
          onConnectionStateChange?.({ status: "disconnected", ws, event });
        },
        onError: (event: Event) => {
          console.error(event);
        },
        onMessage: (event: MessageEvent) => {
          onMessageFromBackend?.(event);
        },
      };
      ws.addEventListener('open', handlers.onOpen);
      ws.addEventListener('close', handlers.onClose);
      ws.addEventListener('error', handlers.onError);
      ws.addEventListener('message', handlers.onMessage);

      // on component unmount
      return () => {
        // remove event listeners
        ws.removeEventListener('open', handlers.onOpen);
        ws.removeEventListener('close', handlers.onClose);
        ws.removeEventListener('error', handlers.onError);
        ws.removeEventListener('message', handlers.onMessage);

        // close connection
        ws.close();
      };
    },
    []
  );

}