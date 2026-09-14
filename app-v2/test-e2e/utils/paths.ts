import * as path from 'node:path';
import * as os from "node:os";

export const utilsPath = {
  getUserAppDataDirPath() {
    switch (process.platform) {
      case "darwin":
        return path.join(os.homedir(), "Library", "Application Support");
      case "win32":
        return process.env.APPDATA ?? path.join(os.homedir(), "AppData");
      case "linux":
        return process.env.XDG_CONFIG_HOME ?? path.join(os.homedir(), ".config");
      default:
        throw new Error(`Unsupported platform: ${process.platform}`);
    }
  }
};