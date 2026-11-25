import { useState } from "react";

/** React State api for {@link FormServerResultAlert} */
export function useFormServerResultApi() {

  const [serverResult, setServerResult] = useState<
    | null
    | { status: "success"; title?: string, message?: string; }
    | { status: "error", title?: string, message?: string; }
  >(null);

  return {
    serverResult,
    setServerResult,
    clearServerResult: () => setServerResult(null),
  };

}
