import { createFileRoute } from '@tanstack/react-router';

import { useMutationUpdateSettings, useSettings, type Settings } from '#/data';

import { SettingsReadonlyForm } from './-components/settings-readonly-form';
import { SettingsMutableForm } from './-components/settings-mutable-form';

import { RootSidebarContentMain, RootSidebarContentTopBar } from '@/components/ui/root';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertTitle } from '#/components/ui/alert';
import { ErrorRenderer } from '#/components/ui/error';
import type React from 'react';

export const Route = createFileRoute('/settings/')({
  component: RouteComponent,
  pendingComponent: RouteComponent,
});

function RouteComponent() {
  const querySettings = useSettings();

  if (querySettings.isLoading) {
    return <ViewLoading />;
  }
  if (querySettings.isError || !querySettings.data) {
    return <ViewError error={querySettings.error} />;
  }
  return (
    <ViewSuccess settings={querySettings.data} />
  );
}

function ViewLoading() {
  return (
    <>
      <RootSidebarContentTopBar>
        <Skeleton className="w-50 h-8" />
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        {null}
      </RootSidebarContentMain>
    </>
  );
}

function ViewError({
  error
}: {
  error: Error | null;
}) {
  return (
    <>
      <RootSidebarContentTopBar>
        <h1>
          Settings
        </h1>
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        <Alert
          aria-label={`Error loading settings`}
          variant="destructive"
        >
          <AlertTitle>
            Error loading settings
          </AlertTitle>
          <ErrorRenderer error={error} />
        </Alert>
      </RootSidebarContentMain>
    </>
  );
}

function ViewSuccess({
  settings
}: {
  settings: Settings;
}) {

  const mutationUpdateSettings = useMutationUpdateSettings();

  const handleUpdateSubmit: React.ComponentProps<typeof SettingsMutableForm>['onSubmit'] = async (formValues) => {
    const result = await mutationUpdateSettings.mutateAsync({
      body: formValues,
    });
    if (result) return { status: 'success', message: 'Settings Updated', };
    return { status: 'error', message: 'Error', };
  };

  return (
    <>
      <RootSidebarContentTopBar>
        <h1 className="font-semibold">
          Settings
        </h1>
      </RootSidebarContentTopBar>
      <RootSidebarContentMain>
        <div className="w-full flex flex-col gap-4">
          <SettingsReadonlyForm
            settingsReadonly={settings.readonly}
          />
          <SettingsMutableForm
            initialValues={settings.mutable}
            onSubmit={handleUpdateSubmit}
          />
        </div>
      </RootSidebarContentMain>
    </>
  );
}