import { useCallback } from "react";
import { Time } from "#/utils/time";
import { useIntervalValue } from "#/hooks/use-interval";

export function TimeDurationMMSS(props: (
  | { type: "ms"; durationInMs: number; }
  | { type: "mm:ss", durationString: string; }
)) {
  const text = props.type === 'mm:ss'
    ? props.durationString
    : new Time(props.durationInMs).asMMSS().full.asString;

  return (
    <span className="min-w-9 text-xs text-muted-foreground break-all text-center">
      {text}
    </span>
  );
}