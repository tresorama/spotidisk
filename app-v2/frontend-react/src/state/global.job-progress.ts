import { atom, useAtomValue, useSetAtom } from "jotai";
import type { WsBackendEvent } from "#/lib/api-client/types";

/** Data as it comes from the backend */
type JobProgressFromBackend = Extract<WsBackendEvent['payload'], { kind: 'JOB_PROGRESS'; }>;

/** Job Progress State (as it comes from the backend) */
type JobProgressStateRaw = null | JobProgressFromBackend;

/** Job Progress State (with derived-on-frontend data) */
type JobProgressStateDerived = null | (
  & NonNullable<JobProgressStateRaw>
  & {
    jobsReverse: NonNullable<JobProgressStateRaw>['jobs'];
  }
);

// atoms
const atomGlobalJobProgressStateRaw = atom<JobProgressStateRaw>(null);
const atomGlobalJobProgressState = atom<JobProgressStateDerived>(get => {
  const raw = get(atomGlobalJobProgressStateRaw);
  if (!raw) return null;
  return {
    ...raw,
    jobsReverse: [...raw.jobs].reverse(),
  };
});

// hooks
export const useGlobalJobProgress = () => useAtomValue(atomGlobalJobProgressState);
export const useGlobalJobProgressActions = () => {
  const setJobProgress = useSetAtom(atomGlobalJobProgressStateRaw);
  return {
    setJobProgress,
  };
};