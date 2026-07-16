import { BrowserWindow } from "electron";
import type { OrchestratorInitProps } from "./orchestrator";
import { MainToLauncherApi } from "./main-to-launcher-api";
import { WebServer } from "./web-server";

/** 
 * Sub Class of {@link Orchestrator} that manages all system parts:
 * - electron launch window
 * - backend process
 * - frontend process/frontend web server 
 * */
export class SystemPartsManager {
  private DEPS: OrchestratorInitProps['DEPS'];
  private DELAY_PAUSE_TO_LET_USER_SEE_UI_CHANGES: number = 1000;

  constructor(DEPS: OrchestratorInitProps['DEPS']) {
    this.DEPS = DEPS;
  }

  /** Create (and launch) Electron window for the LAUNCHER DIALOG and load its HTML */
  public async electronLaunchWindow_start() {
    const { CONSTANTS, INSTANCES, LOGGERS } = this.DEPS;

    LOGGERS.ORC.log('🚀 createElectronLaunchWindow - START');

    // 1. create electron window
    LOGGERS.ORC.log('- Creating Electron window...');
    INSTANCES.electronLaunchWindow = new BrowserWindow({
      width: CONSTANTS.ELECTRON_LAUNCH_WINDOW.WIDTH,
      height: CONSTANTS.ELECTRON_LAUNCH_WINDOW.HEIGHT,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: CONSTANTS.PATHS.FRONTEND_LAUNCH_PRELOAD_JS_PATH,
      },
    });
    INSTANCES.electronLaunchWindow.on('closed', () => {
      INSTANCES.electronLaunchWindow = null;
    });

    // 2. load static launch HTML
    LOGGERS.ORC.log(`- Navigating to Launch HTML at ${CONSTANTS.PATHS.FRONTEND_LAUNCH_INDEX_HTML_PATH}`);
    await INSTANCES.electronLaunchWindow.loadFile(CONSTANTS.PATHS.FRONTEND_LAUNCH_INDEX_HTML_PATH);

    // open dev tools
    if (CONSTANTS.ENV_TYPE === 'dev') {
      LOGGERS.ORC.log('- Enabling dev tools...');
      INSTANCES.electronLaunchWindow.webContents.openDevTools();
    }

    // 3. init the main-to-launcher API class
    LOGGERS.ORC.log('- Creating Main-to-Launcher API...');
    INSTANCES.electronMainToLauncherApi = new MainToLauncherApi({
      electronBrowserWindow: INSTANCES.electronLaunchWindow
    });
    INSTANCES.electronLaunchWindow.on('closed', () => {
      INSTANCES.electronMainToLauncherApi = null;
    });

    // 4. send message to launcher
    INSTANCES.electronMainToLauncherApi.sendMessageToLauncher({
      type: 'log',
      severity: 'info',
      text: `🚀 Initializing SpotiDisk v${CONSTANTS.APP_INFO.APP_VERSION_X_X_X}...`,
    });
    INSTANCES.electronMainToLauncherApi.sendMessageToLauncher({
      type: 'ui-update',
      progress: 5,
      status: 'Initializing SpotiDisk v' + CONSTANTS.APP_INFO.APP_VERSION_X_X_X,
    });
  }

  /** Close Electron window for the LAUNCHER DIALOG */
  public async electronLaunchWindow_stop() {
    const { LOGGERS, INSTANCES } = this.DEPS;
    LOGGERS.ORC.log('- Closing Electron window...');
    INSTANCES.electronLaunchWindow?.close();
  }

  /** Spawn Backend process (backend python) */
  public async backendProcess_start() {
    const { CONSTANTS, LOGGERS, UTILS, INSTANCES } = this.DEPS;

    LOGGERS.ORC.log('🚀 startBackendProcess - START');

    // 1. launch the backend server

    INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
      type: 'ui-update',
      progress: 10,
      status: `${CONSTANTS.LOGGERS_KEYS.BACKEND} - Launching...`,
    });

    // in DEV and in PROD, 
    // launch the backend server (python fastapi webserver)
    // this server will run in background and will be accessed by the react frontend
    // the backend code is bundled in the app (by electron-builder)
    // NOTE: the constants are different for dev and prod
    LOGGERS.ORC.log(`- Starting Backend (Python + FastAPI) with python. Port: ${CONSTANTS.SERVERS.BACKEND_PORT}`);
    INSTANCES.backendProcess = UTILS.SHELL.launchProcess(
      CONSTANTS.PATHS.BACKEND_VENV_BIN_PYTHON_PATH,
      ["main.py"],
      {
        cwd: CONSTANTS.PATHS.BACKEND_DIR_PATH,
        stdio: 'pipe',
        env: CONSTANTS.BACKEND_ENV_VARS,
      }
    );
    INSTANCES.backendProcess.on('error', (err) => {
      LOGGERS.BE.error('❌ Failed to start backend:', err);
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'error',
        text: `${CONSTANTS.LOGGERS_KEYS.BACKEND} ❌ FAILED TO START: ${err.name}: ${err.message}`,
      });
    });
    INSTANCES.backendProcess.stdout?.on('data', (data: Buffer) => {
      const text = data.toString('utf-8').trimEnd();
      LOGGERS.BE.log(text);
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'info',
        text: `${CONSTANTS.LOGGERS_KEYS.BACKEND} ${text}`
      });
    });
    INSTANCES.backendProcess.stderr?.on('data', (data: Buffer) => {
      const text = data.toString('utf-8').trimEnd();
      LOGGERS.BE.error(text);
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'info',
        text: `${CONSTANTS.LOGGERS_KEYS.BACKEND} ${text}`
      });
    });


    // 2. wait for backend to be ready

    const backendIsReady = await UTILS.OS.waitForService(CONSTANTS.SERVERS.BACKEND_URL);
    if (backendIsReady) {
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'info',
        text: `${CONSTANTS.LOGGERS_KEYS.BACKEND} - Backend can be reached at: ${CONSTANTS.SERVERS.BACKEND_URL}`,
      });
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'ui-update',
        progress: 20,
        status: `${CONSTANTS.LOGGERS_KEYS.BACKEND} - Backend Ready`,
      });
      await UTILS.sleep(this.DELAY_PAUSE_TO_LET_USER_SEE_UI_CHANGES);
    }
    else {
      LOGGERS.BE.error('❌ Backend (Python + FastAPI) is not ready');
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'error',
        text: `${CONSTANTS.LOGGERS_KEYS.BACKEND} ❌ CANNOT CONNECT TO BACKEND! APP CANNOT RUN`,
      });
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'ui-update',
        progress: 20,
        status: `${CONSTANTS.LOGGERS_KEYS.BACKEND} ❌ CANNOT CONNECT TO BACKEND! APP CANNOT RUN`,
      });
    }

    LOGGERS.ORC.log('🚀 startBackendProcess - END ✅');

  }

  /** Stop Backend process (backend python) */
  public async backendProcess_stop() {
    const { LOGGERS, UTILS, INSTANCES } = this.DEPS;
    LOGGERS.ORC.log('- Stopping Backend (Python + FastAPI)...');
    UTILS.SHELL.killProcess(INSTANCES.backendProcess);
  }

  /** Spawn Frontend process (frontend react) */
  public async frontendProcess_start() {
    const { CONSTANTS, LOGGERS, UTILS, INSTANCES } = this.DEPS;

    LOGGERS.ORC.log('🚀 startFrontendProcess - START');

    // 1. launch the frontend webserver

    INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
      type: 'ui-update',
      progress: 25,
      status: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} - Launching...`,
    });

    // in DEV
    if (CONSTANTS.ENV_TYPE === 'dev') {
      // 1. run dev servr of vite directly
      LOGGERS.ORC.log('- Starting Frontend (React) with Vite...');
      INSTANCES.frontendProcess = UTILS.SHELL.launchProcess(
        'pnpm', ['run', 'dev'],
        {
          cwd: CONSTANTS.PATHS.FRONTEND_DIR_PATH,
          stdio: 'pipe',
        }
      );
      INSTANCES.frontendProcess.on('error', (err) => {
        LOGGERS.FE.error(err);
        INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
          type: 'log',
          severity: 'error',
          text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} ❌ FAILED TO START: ${err.name}: ${err.message}`,
        });
      });
      INSTANCES.frontendProcess.stdout?.on('data', (data: Buffer) => {
        const text = data.toString('utf-8').trimEnd();
        LOGGERS.FE.log(text);
        INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
          type: 'log',
          severity: 'info',
          text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} ${text}`,
        });
      });
      INSTANCES.frontendProcess.stderr?.on('data', (data: Buffer) => {
        const text = data.toString('utf-8').trimEnd();
        LOGGERS.FE.error(text);
        INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
          type: 'log',
          severity: 'info',
          text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} ${text}`,
        });
      });

    }
    // in PROD
    else {

      // 1. add constants needed by the frontend by replacing the index.html file <script> tag
      // example of th tag content
      /*
      // FRONTEND_CONFIG_START 
      window.FRONTEND_SAFE_ENV_VARS = {
        BACKEND_HTTP_API_URL: "http://localhost:8000",
        BACKEND_WS_API_URL: "ws://localhost:8000",
      }
      // FRONTEND_CONFIG_END 
      */
      LOGGERS.ORC.log('- Adding constants to Frontend index.html (window.FRONTEND_SAFE_ENV_VARS)...');
      await UTILS.DISK.replaceTextInFile({
        filePath: CONSTANTS.PATHS.FRONTEND_INDEX_HTML_PATH,
        toReplaceRegexp: /\/\/ FRONTEND_CONFIG_START(.|\n)*\/\/ FRONTEND_CONFIG_END/g,
        replaceWithText: `
        // FRONTEND_CONFIG_START 
        // Following values:
        // - are injected by ELECTRON-MAIN code at app launch (before serving frontnd spa)
        // - are PROD only
        window.FRONTEND_SAFE_ENV_VARS = ${JSON.stringify(CONSTANTS.FRONTEND_ENV_VARS)}
        // FRONTEND_CONFIG_END
      `,
      });

      // 2. start a webserver to serve the static react spa
      // that must be built (by vite) and then bundled in the app bundle (by electron-builder)
      LOGGERS.ORC.log(`- Starting Frontend (React) with Node.js Webserver. Port: ${CONSTANTS.SERVERS.FRONTEND_PORT}`);
      INSTANCES.frontendWebServer = new WebServer({
        dirPathToServe: CONSTANTS.PATHS.FRONTEND_DIR_PATH,
        port: CONSTANTS.SERVERS.FRONTEND_PORT,
        logger: {
          key: '',
          keyNice: '',
          transports: [],
          log: (text: string) => {
            LOGGERS.FE.log(text);
            INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
              type: 'log',
              severity: 'info',
              text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} ${text}`,
            });
          },
          error: (text: string) => {
            LOGGERS.FE.error(text);
            INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
              type: 'log',
              severity: 'error',
              text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} ${text}`,
            });
          },
        }
      });
      INSTANCES.frontendWebServer.launch();
    }

    // 2. wait for the frontend to be ready
    LOGGERS.ORC.log('- Waiting for Frontend (React) to be ready...');
    const isReady = await UTILS.OS.waitForService(CONSTANTS.SERVERS.FRONTEND_URL);
    if (isReady) {
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'info',
        text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} - Frontend can be reached at: ${CONSTANTS.SERVERS.FRONTEND_URL}`,
      });
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'ui-update',
        progress: 30,
        status: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} - Frontend Ready`,
      });
      await UTILS.sleep(this.DELAY_PAUSE_TO_LET_USER_SEE_UI_CHANGES);
    }
    else {
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'log',
        severity: 'error',
        text: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} - CANNOT CONNECT TO FRONTEND - APP CANNOT START`,
      });
      INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
        type: 'ui-update',
        progress: 30,
        status: `${CONSTANTS.LOGGERS_KEYS.FRONTEND} - CANNOT CONNECT TO FRONTEND - APP CANNOT START`,
      });
    }


    LOGGERS.ORC.log('🚀 startFrontendProcess - END ✅');

  }

  /** Stop the Frontend (React) process */
  public async frontendProcess_stop() {
    const { LOGGERS, UTILS, INSTANCES } = this.DEPS;
    LOGGERS.ORC.log('- Stopping Frontend (React)...');
    UTILS.SHELL.killProcess(INSTANCES.frontendProcess);
  }

  /** Create (and launch) Electron window for the MAIN FRONTEND and navigate to the frontend SPA URL */
  public async electronMainWindow_start() {
    const { CONSTANTS, INSTANCES, LOGGERS, UTILS } = this.DEPS;

    LOGGERS.ORC.log('🚀 createElectronWindow - START');

    INSTANCES.electronMainToLauncherApi?.sendMessageToLauncher({
      type: 'ui-update',
      progress: 100,
      status: 'Launching Electron window...',
    });
    await UTILS.sleep(2000);

    // 1. create electron window
    LOGGERS.ORC.log('- Creating Electron window...');
    INSTANCES.electronMainWindow = new BrowserWindow({
      width: CONSTANTS.ELECTRON_MAIN_WINDOW.WIDTH,
      height: CONSTANTS.ELECTRON_MAIN_WINDOW.HEIGHT,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        // enableRemoteModule: false,
      },
    });
    INSTANCES.electronMainWindow.on('closed', () => {
      INSTANCES.electronMainWindow = null;
    });

    // 2. navigate to the frontend spa index.html
    LOGGERS.ORC.log(`- Navigating to Frontend at ${CONSTANTS.SERVERS.FRONTEND_URL}`);
    INSTANCES.electronMainWindow.loadURL(CONSTANTS.SERVERS.FRONTEND_URL);

    // 3. open dev tools
    if (CONSTANTS.ENV_TYPE === 'dev') {
      LOGGERS.ORC.log('- Enabling dev tools...');
      INSTANCES.electronMainWindow.webContents.openDevTools();
    }

    LOGGERS.ORC.log('🚀 createElectronWindow - END ✅');
  }

  /** Close Electron window for the MAIN FRONTEND */
  public async electronMainWindow_stop() {
    const { LOGGERS, INSTANCES } = this.DEPS;
    LOGGERS.ORC.log('- Closing Electron window...');
    INSTANCES.electronMainWindow?.close();
  }


}