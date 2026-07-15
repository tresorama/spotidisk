import type { BrowserWindow } from "electron";


/** Type of message moved from electron-main to launcher */
export type ElectronMainToLaunchWindow_MessageTypeMap = {
  MESSAGE: "message";
};

/** Payload of data moved from electron- to launcher */
export type ElectronMainToLaunchWindow_MessagePayloads = {
  MESSAGE: (
    | { type: 'ui-update', progress: number, status: string; }
    | { type: 'log', severity: "info" | "error", text: string; }
  );
};


// constants

const MESSAGE_TYPE_MAP: ElectronMainToLaunchWindow_MessageTypeMap = {
  MESSAGE: "message",
};

// main class

/** 
 * Object used to send messages from `electron-main` to `electronWindowLaunch` 
 * (the frontnd of the launchr of the app)  
 * */
export class MainToLauncherApi {
  private electronBrowserWindow: BrowserWindow;

  constructor({
    electronBrowserWindow
  }: {
    electronBrowserWindow: BrowserWindow;
  }) {
    this.electronBrowserWindow = electronBrowserWindow;
  }

  sendMessageToLauncher(data: ElectronMainToLaunchWindow_MessagePayloads['MESSAGE']) {
    this.electronBrowserWindow.webContents.send(MESSAGE_TYPE_MAP.MESSAGE, data);
  }
}