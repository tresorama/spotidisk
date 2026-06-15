import React, { useState } from "react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ProgressBar } from "@/components/ui/progress-bar";

export function ProgressBox({
  className,
  children,
}: {
  className?: React.ComponentProps<"div">["className"];
  children?: React.ReactNode;
}) {
  return (
    <div className={cn("h-60 flex flex-col border rounded-md bg-muted", className)}>
      {children}
    </div>
  );

}

export function ProgressBoxContent({
  debugData,
  title,
  progress,
}: {
  debugData: unknown;
  title?: string;
  /** 0-1 range */
  progress?: number;
}) {
  const [tabKey, setTabKey] = useState<'normal' | 'debug'>('normal');

  return (
    <div className="min-h-0 flex-1 flx flex-col">
      <div className="py-1 px-2 text-xs/none text-muted-foreground border-b">
        {tabKey === 'normal' ? (
          <Button
            onClick={() => setTabKey('debug')}
            variant="link"
            size="xs"
          >
            View Debug
          </Button>
        ) : (
          <Button
            onClick={() => setTabKey('normal')}
            variant="link"
            size="xs"
          >
            Close Debug
          </Button>
        )}
      </div>
      <div className="min-h-0 flex-1 overflow-auto">
        {tabKey === 'normal' ? (
          <div className="p-2 text-xs text-muted-foreground">
            {title && (
              <div className="font-medium">{title}</div>
            )}
            {typeof progress === 'number' && (
              <ProgressBar progress={progress} />
            )}
          </div>
        ) : (
          <pre className="p-2 whitespace-pre-wrap text-xs text-muted-foreground">
            {serializeJsonToString(debugData)}
          </pre>
        )}
      </div>
    </div>
  );
}

export function ProgressBoxBottomBar({ children }: { children?: React.ReactNode; }) {
  return (
    <div className={
      "empty:hidden"
      + " py-1 px-2"
      + " flex gap-2 justify-between items-center"
      + " text-xs/none text-muted-foreground"
      + " border-t"
    }>
      {children}
    </div>
  );
}

function serializeJsonToString(data: unknown) {
  try {
    return JSON.stringify(data, null, 2);
  } catch (error) {
    console.log('Progress Box - serializeJsonToString - Error');
    console.error(error);
    console.log('Progress Box - serializeJsonToString - Input Data');
    console.log(data);
    return "Invalid JSON";
  }
}