import { useState } from "react";
import { CheckCircle2Icon, CircleXIcon } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

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

/** React component that renders an alert for {@link useFormServerResultApi} */
export function FormServerResultAlert({
  formServerResultApi,
}: {
  formServerResultApi: ReturnType<typeof useFormServerResultApi>,
}) {

  if (formServerResultApi.serverResult === null) {
    return;
  }

  if (formServerResultApi.serverResult.status === 'success') {
    return (
      <Alert variant="success">
        <CheckCircle2Icon />
        <AlertTitle>
          {formServerResultApi.serverResult.title ?? "Form Submitted Successfully!"}
        </AlertTitle>
        {formServerResultApi.serverResult.message && (
          <AlertDescription className="whitespace-pre">
            {formServerResultApi.serverResult.message}
          </AlertDescription>
        )}
      </Alert>
    );
  }

  // error
  return (
    <Alert variant="destructive">
      <CircleXIcon />
      <AlertTitle>
        {formServerResultApi.serverResult.title ?? "Form Submitted with Error!"}
      </AlertTitle>
      {formServerResultApi.serverResult.message && (
        <AlertDescription className="whitespace-pre">
          {formServerResultApi.serverResult.message}
        </AlertDescription>
      )}
    </Alert>
  );

}