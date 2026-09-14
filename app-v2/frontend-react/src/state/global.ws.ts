import { atom, useAtomValue, useSetAtom } from "jotai";

const atomGlobalWSConnectionStatus = atom<null | "connecting" | "connected" | "disconnected">(null);

export const useGlobalWebSocketConnection = () => {
  const status = useAtomValue(atomGlobalWSConnectionStatus);
  return { status };
};

export const useGlobalWebSocketConnectionActions = () => {
  const setStatus = useSetAtom(atomGlobalWSConnectionStatus);
  return {
    setStatus,
  };
};