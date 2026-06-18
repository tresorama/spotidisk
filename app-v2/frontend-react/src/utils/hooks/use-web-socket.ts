import { useEffect } from "react";

export function useWebSocketConnection({
  initWsConnection,
  onConnected,
  onDisconnected,
  onMessageFromBackend,
}: {
  initWsConnection: () => WebSocket;
  onConnected?: (ws: WebSocket) => void;
  onDisconnected?: (ws: WebSocket) => void;
  onMessageFromBackend?: (event: MessageEvent<any>) => void;
}) {
  useEffect(
    () => {
      const ws = initWsConnection();
      ws.onopen = () => {
        onConnected?.(ws);
      };
      ws.onclose = () => {
        onDisconnected?.(ws);
      };
      ws.onmessage = (event) => {
        onMessageFromBackend?.(event);
      };
      const closeConnectionFromFrontend = () => {
        ws.close();
      };
      return closeConnectionFromFrontend;
    },
    []
  );

  return null;
}