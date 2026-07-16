import path from "node:path";
import { app } from "electron";
import configJson from "../config.json";
import packageJson from "../package.json";
import { utilsOs } from "./utils/os";
import { utilsPath } from "./utils/path";

import type { EnvVarsInput as FrontendEnvVarsProd } from "../../app-v2/frontend-react/src/constants/input-env-vars.type";

/** App Constants */
export type Constants = Awaited<ReturnType<typeof createConstants>>;

export async function createConstants() {

  const IS_DEV = process.env.NODE_ENV === 'development' || !app.isPackaged;

  // 1. define constants shared in both DEV and PROD

  const SHARED_CONSTANTS = {
    /** General app info like name, version, author... */
    APP_INFO: {
      APP_NAME: "SpotiDisk",
      APP_VERSION_X_X_X: packageJson.version,
      CREATOR: `${packageJson.author.name} ${packageJson.author.url} ${packageJson.author.email}`,
    },
    /** OS info (platform, arch) */
    OS: utilsOs.getOSInfo(),
    /** 
     * Electron runtime info (node.js version).  
     * NOTE: Electron bundles a modified version of Node.js, the app won't use system Node.js
     * */
    ELECTRON_RUNTIME: {
      VERSIONS: process.versions.node
    },
    /** Configuration for the electron window `launch` (the app initialization dialog) */
    ELECTRON_LAUNCH_WINDOW: {
      WIDTH: configJson.electronLaunchWindow.width,
      HEIGHT: configJson.electronLaunchWindow.height,
    },
    /** Configuration for the electron window `main` (the app frontend) */
    ELECTRON_MAIN_WINDOW: {
      WIDTH: configJson.electronMainWindow.width,
      HEIGHT: configJson.electronMainWindow.height,
    },
    /** Logger keys */
    LOGGERS_KEYS: {
      ORCHESTRATOR: '🚐 ORCHESTRATOR',
      BACKEND: '🏠 BACKEND',
      FRONTEND: '🧩 FRONTEND',
    }
  } as const;

  // 2. define constants based on env

  // Development: usa i percorsi reali
  // Production: backend/frontend è dentro il bundle dell'app

  // dev
  if (IS_DEV) {
    const BACKEND_PORT = 8000;
    const FRONTEND_PORT = 3000;

    return {
      ENV_TYPE: 'dev',
      ...SHARED_CONSTANTS,
      /** Paths to parts of the app (frontend, backend, log files...) */
      PATHS: {
        USER_HOME_PATH: utilsPath.getUserHomeDir(),
        USER_DESKTOP_PATH: utilsPath.getUserDesktopDir(),
        CWD: utilsPath.getCWD(),
        APP: undefined,
        BACKEND_DIR_PATH: path.join(__dirname, '../../app-v2/backend-python'),
        BACKEND_VENV_ACTIVATE_PATH: path.join(__dirname, '../../app-v2/backend-python/.venv/bin/activate'),
        BACKEND_VENV_BIN_PYTHON_PATH: path.join(__dirname, '../../app-v2/backend-python/.venv/bin/python'),
        FRONTEND_DIR_PATH: path.join(__dirname, '../../app-v2/frontend-react'),
        FRONTEND_LAUNCH_INDEX_HTML_PATH: path.join(__dirname, '../src/frontend-launch/index.html'),
        FRONTEND_LAUNCH_PRELOAD_JS_PATH: path.join(__dirname, '../src/frontend-launch/preload.js'),
        LOG_FILE_PATH: path.join(utilsPath.getUserDesktopDir(), `/SPOTIDISK-LOGS/log--${new Date().toISOString()}.txt`),
        LOG_FILE_PATH_2: path.join(utilsPath.getUserHomeDir(), `.spotidisk/logs/${new Date().toISOString()}.txt`),
      },
      /** Server ports */
      SERVERS: {
        BACKEND_PORT: BACKEND_PORT,
        BACKEND_URL: `http://localhost:${BACKEND_PORT}`,
        FRONTEND_PORT: FRONTEND_PORT,
        FRONTEND_URL: `http://localhost:${FRONTEND_PORT}`,
      },
    } as const;
  }

  // prod
  const BACKEND_PORT = await utilsOs.getFreePort();
  const FRONTEND_PORT = await utilsOs.getFreePort();

  return {
    ENV_TYPE: 'prod',
    ...SHARED_CONSTANTS,
    /** Paths to parts of the app (frontend, backend, log files...) */
    PATHS: {
      USER_HOME_PATH: utilsPath.getUserHomeDir(),
      USER_DESKTOP_PATH: utilsPath.getUserDesktopDir(),
      CWD: utilsPath.getCWD(),
      APP: path.join(process.resourcesPath, 'app'),
      BACKEND_DIR_PATH: path.join(process.resourcesPath, 'app/dist-backend'),
      BACKEND_VENV_ACTIVATE_PATH: path.join(process.resourcesPath, 'app/dist-backend/.venv/bin/activate'),
      BACKEND_VENV_BIN_PYTHON_PATH: path.join(process.resourcesPath, 'app/dist-backend/.venv/bin/python'),
      FRONTEND_DIR_PATH: path.join(process.resourcesPath, 'app/dist-frontend/client'),
      FRONTEND_INDEX_HTML_PATH: path.join(process.resourcesPath, 'app/dist-frontend/client/index.html'),
      FRONTEND_LAUNCH_INDEX_HTML_PATH: path.join(process.resourcesPath, 'app/dist-frontend-launch/index.html'),
      FRONTEND_LAUNCH_PRELOAD_JS_PATH: path.join(process.resourcesPath, 'app/dist-frontend-launch/preload.js'),
      LOG_FILE_PATH: path.join(utilsPath.getUserDesktopDir(), `/SPOTIDISK-LOGS/log--${new Date().toISOString()}.txt`),
      LOG_FILE_PATH_2: path.join(utilsPath.getUserHomeDir(), `.spotidisk/logs/${new Date().toISOString()}.txt`),
    },
    /** Server ports */
    SERVERS: {
      BACKEND_PORT: BACKEND_PORT,
      BACKEND_URL: `http://localhost:${BACKEND_PORT}`,
      FRONTEND_PORT: FRONTEND_PORT,
      FRONTEND_URL: `http://localhost:${FRONTEND_PORT}`,
    },
    /** Environment variables that must be passed to the frontend SPA */
    FRONTEND_ENV_VARS: {
      BACKEND_HTTP_API_URL: `http://localhost:${BACKEND_PORT}`,
      BACKEND_WS_API_URL: `ws://localhost:${BACKEND_PORT}`,
      APP_VERSION: SHARED_CONSTANTS.APP_INFO.APP_VERSION_X_X_X,
      FRONTEND_APP_MODE: "PROD",
      FRONTEND_URL: `http://localhost:${FRONTEND_PORT}`,
    } satisfies FrontendEnvVarsProd
  } as const;
}