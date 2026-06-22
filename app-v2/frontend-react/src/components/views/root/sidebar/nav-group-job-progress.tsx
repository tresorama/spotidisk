import { useGlobalJobProgress } from "#/state/global.job-progress";
import { useGlobalWebSocket } from "#/state/global.ws";
import { useMutationJobDemoStart } from "#/data/use-playlists";

import {
  ProgressBox,
  ProgressBoxBottomBar,
  ProgressBoxContent,
  ProgressBoxContentJob,
  ProgressBoxContentNoJobs,
} from "#/components/ui/progress-box";
import { Button } from "#/components/ui/button";
import { IconIsInvalid, IconIsValid } from "#/components/ui/icons-common";

export function NavGroupJobProgress() {
  const globalWs = useGlobalWebSocket();
  const jobProgress = useGlobalJobProgress();
  const mutationJobDemoStart = useMutationJobDemoStart();

  return (
    <ProgressBox className="mx-3 h-45">
      <ProgressBoxContent
        debugData={jobProgress}
      >
        {jobProgress.jobs.length === 0 ? (
          <ProgressBoxContentNoJobs />
        ) : jobProgress.jobs.map((job, index) => (
          <ProgressBoxContentJob
            key={index}
            title={job.title}
            status={job.executionStatus}
            progress={job.progress}
            stepsTotal={job.stepsTotal}
            stepsCompleted={job.stepsCompleted}
            messages={job.messages}
          />
        ))}
      </ProgressBoxContent>
      <ProgressBoxBottomBar>
        {globalWs.isConnected ? (
          <div className="flex items-center gap-1 text-xs text-green-500">
            <IconIsValid className="size-[1em]" />
            <span>Connected</span>
          </div>
        ) : (
          <div className="flex items-center gap-1 text-xs text-destructive">
            <IconIsInvalid className="size-[1em]" />
            <span>Disconnected</span>
          </div>
        )}
        <Button
          onClick={() => mutationJobDemoStart.mutate()}
          isLoading={mutationJobDemoStart.isPending}
          disabled={mutationJobDemoStart.isPending}
          variant="link"
          size="xs"
        >
          Job Demo - Start
        </Button>
      </ProgressBoxBottomBar>
    </ProgressBox>
  );
}