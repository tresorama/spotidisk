import { HardDriveIcon } from "lucide-react";

import {
  useMutationUtilsDiskRevealInFinder,
  type Settings,
} from "#/data";

import { FieldGroup, Field, FieldLabel, FieldDescription } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type SettingsReadonlyFormProps = {
  settingsReadonly: Settings['readonly'],
};

export function SettingsReadonlyForm(
  props: SettingsReadonlyFormProps
) {
  return (
    <Card aria-label="Settings Readonly">
      <CardHeader>
        <CardTitle>
          Settings Readonly
        </CardTitle>
        <CardDescription>
          Those settings are readonly, you cannot change them!
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TheForm {...props} />
      </CardContent>
    </Card>
  );
}

function TheForm({
  settingsReadonly
}: SettingsReadonlyFormProps) {

  const mutationUtilDiskRevealInFinder = useMutationUtilsDiskRevealInFinder();

  const fieldsIds = {
    user_config_file_path: "user_config_file_path",
    binary_deno_file_path: "binary_deno_file_path",
    binary_ffmpeg_file_path: "binary_ffmpeg_file_path",
  };

  return (
    <FieldGroup>

      <Field>
        <FieldLabel htmlFor={fieldsIds.user_config_file_path}>
          User config file path
        </FieldLabel>
        <div className="flex-1 flex gap-2">
          <Input
            id={fieldsIds.user_config_file_path}
            readOnly
            value={settingsReadonly.user_config_file_path}
          />
          <Button
            onClick={() => {
              mutationUtilDiskRevealInFinder.mutate({
                body: { path: settingsReadonly.user_config_file_path }
              });
            }}
            isLoading={mutationUtilDiskRevealInFinder.isPending}
            disabled={mutationUtilDiskRevealInFinder.isPending}
            variant="secondary"
          >
            <HardDriveIcon />
            Reveal
          </Button>
        </div>
        <FieldDescription>
          This is the path to the user config file.
          <br />This file is the DataBase of the app.
          <br />IMPORTANT: Backup this file!
        </FieldDescription>
      </Field>

      <Field>
        <FieldLabel htmlFor={fieldsIds.binary_deno_file_path}>
          Binary Deno file path
        </FieldLabel>
        <div className="flex-1 flex gap-2">
          <Input
            id={fieldsIds.binary_deno_file_path}
            readOnly
            value={settingsReadonly.binary_deno_file_path}
          />
          {/* <Button
            onClick={() => mutationUtilDiskRevealInFinder.mutate({
              path: settingsReadonly.user_config_file_path
            })}
            isLoading={mutationUtilDiskRevealInFinder.isPending}
            disabled={mutationUtilDiskRevealInFinder.isPending}
            variant="secondary"
          >
            <HardDriveIcon />
            Reveal
          </Button> */}
        </div>
        <FieldDescription>
          This is the path to the deno binary file used by the backend.
        </FieldDescription>
      </Field>

      <Field>
        <FieldLabel htmlFor={fieldsIds.binary_ffmpeg_file_path}>
          Binary FFMPEG file path
        </FieldLabel>
        <div className="flex-1 flex gap-2">
          <Input
            id={fieldsIds.binary_ffmpeg_file_path}
            readOnly
            value={settingsReadonly.binary_ffmpeg_file_path}
          />
          {/* <Button
            onClick={() => mutationUtilDiskRevealInFinder.mutate({
              path: settingsReadonly.user_config_file_path
            })}
            isLoading={mutationUtilDiskRevealInFinder.isPending}
            disabled={mutationUtilDiskRevealInFinder.isPending}
            variant="secondary"
          >
            <HardDriveIcon />
            Reveal
          </Button> */}
        </div>
        <FieldDescription>
          This is the path to the ffmpeg binary file used by the backend.
        </FieldDescription>
      </Field>

    </FieldGroup>
  );

}