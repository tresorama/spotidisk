// utils

function millisToMinutesAndSeconds(millis: number) {
  const minutes = Math.floor(millis / 60000);
  const seconds = Number(((millis % 60000) / 1000).toFixed(0));
  return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}

// components

export function TimeDurationMMSS(props: (
  | { type: "ms"; durationInMs: number; }
  | { type: "mm:ss", durationString: string; }
)) {
  const text = props.type === 'mm:ss' ? props.durationString : millisToMinutesAndSeconds(props.durationInMs);
  return (
    <span className="min-w-9 text-xs text-muted-foreground break-all text-center">
      {text}
    </span>
  );
}