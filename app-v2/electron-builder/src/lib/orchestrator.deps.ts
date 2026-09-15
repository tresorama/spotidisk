import type { BrowserWindow } from "electron";

import { type Constants } from "../constants";
import { Logger, LoggerTransportConsole, LoggerTransportFile } from "./logger";
import type { WebServer } from "./web-server";
import type { MainToLauncherApi } from "./main-to-launcher-api";

import { utilsDisk } from "../utils/disk";
import { utilsOs } from "../utils/os";
import { utilsShell } from "../utils/shell";
import { utilsString } from "../utils/string";
import { utilsPath } from "../utils/path";
import { sleep } from "../utils/sleep";

export type OrchestratorDeps = Awaited<ReturnType<typeof createOrchestratorDeps>>;

export async function createOrchestratorDeps({
  electronApp,
  constants,
}: {
  electronApp: Electron.App;
  constants: Constants;
}) {

  const CONSTANTS = constants;

  const LOGGERS = (() => {
    const LOGGER_TRANSPORTS = {
      FILE_ALL: new LoggerTransportFile(CONSTANTS.PATHS.LOG_FILE_PATH),
      CONSOLE_ORC: new LoggerTransportConsole({ color: 'blue' }),
      CONSOLE_BE: new LoggerTransportConsole({ color: 'green' }),
      CONSOLE_FE: new LoggerTransportConsole({ color: 'yellow' }),
    };

    return {
      ORC: new Logger({
        key: CONSTANTS.LOGGERS_KEYS.ORCHESTRATOR,
        transports: [LOGGER_TRANSPORTS.FILE_ALL, LOGGER_TRANSPORTS.CONSOLE_ORC]
      }),
      BE: new Logger({
        key: CONSTANTS.LOGGERS_KEYS.BACKEND,
        transports: [LOGGER_TRANSPORTS.FILE_ALL, LOGGER_TRANSPORTS.CONSOLE_BE]
      }),
      FE: new Logger({
        key: CONSTANTS.LOGGERS_KEYS.FRONTEND,
        transports: [LOGGER_TRANSPORTS.FILE_ALL, LOGGER_TRANSPORTS.CONSOLE_FE]
      }),
    };

  })();

  const UTILS = {
    OS: utilsOs,
    SHELL: utilsShell,
    STRING: utilsString,
    DISK: utilsDisk,
    PATH: utilsPath,
    sleep,
  };

  const INSTANCES: {
    /** instance of Electron App (always available) */
    electronApp: Electron.App,
    /** child process of backend server launched */
    backendProcess: ReturnType<typeof UTILS['SHELL']['launchProcess']> | null,
    /** child process of frontend server launched (used in dev to run vite directly) */
    frontendProcess: ReturnType<typeof UTILS['SHELL']['launchProcess']> | null,
    /** instance of frontend webserver (used in prod to serve the static react SPA) */
    frontendWebServer: WebServer | null,
    /** instance of Electron WebView (browser window) used to render the frontend (frontend react) */
    electronMainWindow: BrowserWindow | null;
    /** instance of Electron WebView (browser window) used to render launch dialog (static html) */
    electronLaunchWindow: BrowserWindow | null;
    /** instance used to send messages from the main app to the launch dialog */
    electronMainToLauncherApi: MainToLauncherApi | null;
  } = {
    electronApp,
    backendProcess: null,
    frontendProcess: null,
    frontendWebServer: null,
    electronMainWindow: null,
    electronLaunchWindow: null,
    electronMainToLauncherApi: null,
  };

  return {
    CONSTANTS,
    LOGGERS,
    UTILS,
    INSTANCES,
  };
}
