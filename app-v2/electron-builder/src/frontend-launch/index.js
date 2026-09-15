// This code runs in the browser page


// ==============================================
// init dom api
// ==============================================

const domApi = (() => {

  const SELECTORS = {
    STATUS: ".status",
    LOGS: ".logs",
    LOG_LINE: ".logs__line",
    PROGRESS: ".progress",
    PROGRESS_PERCENT: ".progress__percent",
    SPINNER: ".spinner",
  };

  const els = {
    /** @type {HTMLDivElement | null} */
    status: document.querySelector(SELECTORS.STATUS),
    /** @type {HTMLDivElement | null} */
    logs: document.querySelector(SELECTORS.LOGS),
    /** @type {HTMLDivElement | null} */
    progress: document.querySelector(SELECTORS.PROGRESS),
    /** @type {HTMLDivElement | null} */
    progressPercent: document.querySelector(SELECTORS.PROGRESS_PERCENT),
    /** @type {HTMLDivElement | null} */
    spinner: document.querySelector(SELECTORS.SPINNER),
  };
  if (!els.status) throw new Error("Missing status element");
  if (!els.logs) throw new Error("Missing logs element");
  if (!els.progress) throw new Error("Missing progress element");
  if (!els.progressPercent) throw new Error("Missing progress percent element");
  if (!els.spinner) throw new Error("Missing spinner element");

  return {
    appendLog(
      /** @type {string} */
      text,
      /** @type {"info" | "error"} */
      type = "info"
    ) {
      // derive text
      // const finalText = `[{{TIMESTAMP}}] {{MSG}}`
      //   .replace("{{TIMESTAMP}}", new Date().toLocaleTimeString())
      //   .replace("{{MSG}}", text);
      const finalText = `{{MSG}}`
        .replace("{{MSG}}", text);
      // create dom el
      const line = document.createElement("div");
      line.className = `logs__line ${type}`;
      line.textContent = finalText;
      // append
      els.logs.appendChild(line);
      els.logs.scrollTop = els.logs.scrollHeight;
    },
    updateProgress(
      /** @type {number} */
      value
    ) {
      els.progress.style.setProperty("--progress-value", value);
      els.progressPercent.textContent = value;
    },
    updateStatus(
      /** @type {string} */
      text
    ) {
      els.status.textContent = text;
    },
    hideSpinner() {
      els.spinner.style.display = "none";
    }
  };

})();


// ==============================================
// init communication to main process
// ==============================================

// import types

/** 
 * @typedef {import("./preload.js").LaunchWindowToElectronMainApiTypes} LaunchWindowToElectronMainApiTypes 
*/


// retrieve api from window

/** @type {LaunchWindowToElectronMainApiTypes['API']} */
const api = (() => {

  /** @type {LaunchWindowToElectronMainApiTypes['WINDOW_OBJECT_KEY']} */
  const WINDOW_OBJECT_KEY = "launchWindowToElectronMainApi";

  if (!window[WINDOW_OBJECT_KEY]) {
    throw new Error(`Missing "${WINDOW_OBJECT_KEY}" window object`);
  }

  /** @type {LaunchWindowToElectronMainApiTypes['API']} */
  const api = window[WINDOW_OBJECT_KEY];

  return api;
})();

// subscribe to messages received from electron-main

api.onMessage(data => {
  if (data.type === 'ui-update') {
    domApi.updateStatus(data.status);
    domApi.updateProgress(data.progress);
    return;
  }
  if (data.type === 'log') {
    domApi.appendLog(data.text, data.severity);
    return;
  }
});