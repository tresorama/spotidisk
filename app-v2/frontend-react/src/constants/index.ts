
import { isBrowser } from "#/utils/runtime";
import type { EnvVarsInput } from "./input-env-vars.type.d.ts";
import { schemaEnvVarsInput } from "./input-env-vars.schema";
import { INPUT_ENV_VARS_DEV } from "./input-env-vars.dev.ts";

// input env vars

export type { EnvVarsInput };

// constants

export type Constants = typeof CONSTANTS;

export const CONSTANTS = (
  isBrowser()
    // In browser,
    // read them from window object, that is augmented by src/routes/__root > CONFIG_INIT_SCRIPT
    // NOTE: In DEV (vite), the window.FRONTEND_SAFE_ENV_VARS is defined by src/routes/__root > CONFIG_INIT_SCRIPT
    // NOTE: In PROD (electron bundle), the window.FRONTEND_SAFE_ENV_VARS is overwritted by electron main before launch
    ? schemaEnvVarsInput.parse(
      // @ts-expect-error
      window.FRONTEND_SAFE_ENV_VARS
    )
    // In server (pnpm build > prerender SPA),
    // use placeholder
    // NOTE: this app is a SPA, the server runtime is only used for prerendering
    : INPUT_ENV_VARS_DEV
);

console.log('CONSTANTS', CONSTANTS);