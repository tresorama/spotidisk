import { utilsPath } from "./utils/paths.ts";

export const CONSTANTS = (() => {
  const base = {
    BACKEND_PORT: '8000',
    FRONTEND_PORT: '3000',
    BACKEND_LOG_LEVEL: "info",
    BACKEND_APP_MODE: "test-e2e",
    BACKEND_DB_FILE_PATH: utilsPath.getUserAppDataDirPath() + "/SpotiDisk/config_test_e2e.json",
  };

  return {
    ...base,
    FRONTEND_URL: `http://localhost:${base.FRONTEND_PORT}`,
  };

})();

const logger = (() => {
  let timesLogged = 0;
  return {
    log: () => {
      if (timesLogged === 0) {
        console.log('CONSTANTS', CONSTANTS);
        timesLogged++;
      }
    }
  };
})();
logger.log();