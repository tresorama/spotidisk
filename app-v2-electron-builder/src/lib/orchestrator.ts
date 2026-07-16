import { Menu, type MenuItemConstructorOptions } from "electron";
import type { OrchestratorDeps } from "./orchestrator.deps";
import { SystemPartsManager } from "./orchestrator.system-parts-manager";

/** Props needed to initialize `new Orchestrator` */
export type OrchestratorInitProps = {
  DEPS: OrchestratorDeps;
};

/**
 * Main class of the App.  
 * This controls the elctron instanc and coordinates the system parts:
 * - electron launch window
 * - backend process
 * - frontend process
 */
export class Orchestrator {
  private DEPS: OrchestratorInitProps['DEPS'];
  private systemPartsManager: SystemPartsManager;

  constructor({
    DEPS,
  }: OrchestratorInitProps) {
    this.DEPS = DEPS;
    this.systemPartsManager = new SystemPartsManager(DEPS);
  }

  /** 
   * Main public function of this class.  
   * You must call this function on `electronApp.on('ready')`  
   * This will initalize all `electronApp` event handlers callback
   * */
  async initializeElectronApp() {
    const { INSTANCES, CONSTANTS } = this.DEPS;

    await this.launchAllSystemParts();

    INSTANCES.electronApp.on('activate', async () => {
      await this.relaunchElectronMainWindow();
    });

    INSTANCES.electronApp.on('window-all-closed', async () => {
      await this.stopAllSystemParts();
      if (CONSTANTS.OS.platform !== 'darwin') {
        INSTANCES.electronApp.quit();
      }
    });

    INSTANCES.electronApp.on('before-quit', async () => {
      await this.stopAllSystemParts();
    });

  }

  // electron lifecycle callbacks

  /** Callback of `app.on('ready')` */
  private async launchAllSystemParts() {
    const { LOGGERS, CONSTANTS } = this.DEPS;

    LOGGERS.ORC.log('🚀 onAppInit - START');
    LOGGERS.ORC.log('\nCONSTANTS:\n' + JSON.stringify(CONSTANTS, null, 2));
    LOGGERS.ORC.log(`App is in "${CONSTANTS.ENV_TYPE.toUpperCase()}" mode`);
    await this.systemPartsManager.electronLaunchWindow_start();
    await this.systemPartsManager.backendProcess_start();
    await this.systemPartsManager.frontendProcess_start();
    await this.systemPartsManager.electronMainWindow_start();
    await this.systemPartsManager.electronLaunchWindow_stop();
    LOGGERS.ORC.log('🚀 onAppInit - END ✅');

  }

  /** Callback of `app.on('window-all-closed')` */
  private async stopAllSystemParts() {
    const { LOGGERS } = this.DEPS;

    LOGGERS.ORC.log('🚀 onAppStop - START');
    await this.systemPartsManager.backendProcess_stop();
    await this.systemPartsManager.frontendProcess_stop();
    await this.systemPartsManager.electronMainWindow_stop();
    await this.systemPartsManager.electronLaunchWindow_stop();
    LOGGERS.ORC.log('🚀 onAppStop - END ✅');
  }

  /** Callback of `app.on('activate')` */
  private async relaunchElectronMainWindow() {
    const { INSTANCES } = this.DEPS;

    if (!INSTANCES.electronMainWindow) {
      await this.systemPartsManager.electronMainWindow_start();
    }
  }

}