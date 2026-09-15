// This code runs in electron-main process
// and is used to expose an API to the window object of the frontnd html page

const { contextBridge, ipcRenderer } = require("electron");

// import types

/** 
 * @typedef {import("../lib/main-to-launcher-api.ts").ElectronMainToLaunchWindow_MessageTypeMap} ElectronMainToLaunchWindow_MessageTypeMap
 * @typedef {import("../lib/main-to-launcher-api.ts").ElectronMainToLaunchWindow_MessagePayloads} ElectronMainToLaunchWindow_MessagePayloads
*/

// define types

/**
 * @typedef {{
 *   WINDOW_OBJECT_KEY: "launchWindowToElectronMainApi",
 *   MESSAGE_TYPE_MAP: ElectronMainToLaunchWindow_MessageTypeMap,
 *   MESSAGE_PAYLOADS: ElectronMainToLaunchWindow_MessagePayloads,
 *   API: {
 *     onMessage: (callback: (message: ElectronMainToLaunchWindow_MessagePayloads['MESSAGE']) => void) => void
 *   }
 * }} LaunchWindowToElectronMainApiTypes
 */

// define constants

/** @type {LaunchWindowToElectronMainApiTypes['WINDOW_OBJECT_KEY']} */
const WINDOW_OBJECT_KEY = "launchWindowToElectronMainApi";

/** @type {LaunchWindowToElectronMainApiTypes['MESSAGE_TYPE_MAP']} */
const MESSAGE_TYPE_MAP = {
  MESSAGE: "message",
};

/** @type {LaunchWindowToElectronMainApiTypes['API']} */
const launchWindowToElectronMainApi = {
  onMessage(callback) {
    ipcRenderer.on(
      MESSAGE_TYPE_MAP.MESSAGE,
      (_, /** @type {LaunchWindowToElectronMainApiTypes['MESSAGE_PAYLOADS']['MESSAGE']} */ message) => {
        callback(message);
      }
    );
  },
};


// Add a window.launchWindowToElectronMainApi object to the global scope of the index.html file
// This is the API that renderer processes use to communicate with the main process
contextBridge.exposeInMainWorld(WINDOW_OBJECT_KEY, launchWindowToElectronMainApi);