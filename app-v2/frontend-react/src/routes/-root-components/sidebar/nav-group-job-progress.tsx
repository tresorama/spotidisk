import { useMutationDemoJobDemoStart } from "#/data";

import { useGlobalJobProgress } from "#/state/global.job-progress";
import { useGlobalWebSocketConnection } from "#/state/global.ws";

import {
  ProgressBoxWrapper,
  ProgressBoxTopBar,
  ProgressBoxBottomBar,
  ProgressBoxContent,
  ProgressBoxContentJob,
  ProgressBoxContentNoJobs,
} from "#/components/ui/progress-box";
import { Button } from "#/components/ui/button";
import { IconIsInvalid, IconIsValid } from "#/components/ui/icons-common";
import { DebugOnly } from "#/components/ui/debug.with-state";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "#/components/ui/collapsible";
import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel } from "#/components/ui/sidebar";
import { CollapsibleIconChevron } from "#/components/ui/collapsible.extra";
import { LoaderIcon } from "lucide-react";

export function AppSidebarNavGroupJobProgress() {
  return (
    <Collapsible defaultOpen>
      <SidebarGroup
        role="group"
        aria-label="Sidebar Group Job Progress"
        className="mt-auto"
      >
        <SidebarGroupLabel
          render={<CollapsibleTrigger />}
          aria-label="Jobs List Toggler"
        >
          Jobs
          <CollapsibleIconChevron />
        </SidebarGroupLabel>
        <CollapsibleContent>
          <SidebarGroupContent>
            <GroupContent />
          </SidebarGroupContent>
        </CollapsibleContent>
      </SidebarGroup>
    </Collapsible>
  );
}

function GroupContent() {

  // global state
  const jobProgress = useGlobalJobProgress();

  // server mutation
  const mutationDemoJobDemoStart = useMutationDemoJobDemoStart();

  return (
    <ProgressBoxWrapper className="mx-3 h-45 lg:h-[28dvh]">
      <DebugOnly>
        <ProgressBoxTopBar />
      </DebugOnly>
      <ProgressBoxContent debugData={jobProgress}>
        {!jobProgress || jobProgress.jobsReverse.length === 0 ? (
          <ProgressBoxContentNoJobs
            role="group"
            aria-label="Jobs List"
          />
        ) : jobProgress.jobsReverse.map(job => (
          <ProgressBoxContentJob
            key={job.id}
            role="group"
            aria-label={job.title}
            id={job.id}
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
        <BadgeWSConnectionStatus />
        <DebugOnly>
          <Button
            onClick={() => mutationDemoJobDemoStart.mutate()}
            isLoading={mutationDemoJobDemoStart.isPending}
            disabled={mutationDemoJobDemoStart.isPending}
            variant="link"
            size="xs"
          >
            Job Demo - Start
          </Button>
        </DebugOnly>
      </ProgressBoxBottomBar>
    </ProgressBoxWrapper>
  );
}

function BadgeWSConnectionStatus() {

  // global state
  const globalWs = useGlobalWebSocketConnection();

  return (
    <div
      role="group"
      aria-label="Global WS Connection Status"
      data-status={globalWs.status}
      className={
        "flex items-center gap-1 text-xs"
        + " data-[status=connected]:text-green-500"
        + " data-[status=connecting]:text-muted-foreground"
        + " data-[status=disconnected]:text-destructive"
      }
    >
      {
        globalWs.status === 'connected' ? (
          <>
            <IconIsValid className="size-[1em]" />
            <span>Connected</span>
          </>
        ) : globalWs.status === 'disconnected' ? (
          <>
            <IconIsInvalid className="size-[1em]" />
            <span>Disconnected</span>
          </>
        ) : (
          <>
            <LoaderIcon className="size-[1em] animate-spin" />
            <span>Connecting</span>
          </>
        )
      }
    </div>
  );
}