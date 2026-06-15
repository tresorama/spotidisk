import { useEffect, useState } from "react";

export function useWebSocket<TData>({
  initWsConnection,
}: {
  initWsConnection: () => WebSocket;
}) {
  const [connectionStatus, setConnectionStatus] = useState<'Connected' | 'Closed'>('Closed');
  const [data, setData] = useState<null | TData>(null);

  useEffect(
    () => {
      const ws = initWsConnection();

      ws.onmessage = (event) => { setData(JSON.parse(event.data)); };
      ws.onopen = () => { setConnectionStatus('Connected'); };
      ws.onclose = () => { setConnectionStatus('Closed'); };
      const closeConnectionFromFrontend = () => { ws.close(); };

      return closeConnectionFromFrontend;
    },
    []
  );

  return { connectionStatus, data };
}