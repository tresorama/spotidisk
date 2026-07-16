import fs from "node:fs";
import path from "node:path";
import nodeUtil from "node:util";

// main class

export class Logger {
  key: string;
  transports: LoggerTransport[];
  constructor({
    key,
    transports,
  }: {
    key: string;
    transports: LoggerTransport[],
  }) {
    this.key = key;
    this.transports = transports;
  }

  get keyNice() {
    return `[${this.key}]`;
  }
  log(...args: Parameters<typeof console.log>) {
    this.transports.forEach(t => t.printLog(this.keyNice, ...args));
  }
  error(...args: Parameters<typeof console.error>) {
    this.transports.forEach(t => t.printLog(this.keyNice, ...args));
  }
}

// transport

export type LoggerTransport = {
  printLog: (key: string, ...args: Parameters<typeof console.log>) => void;
};

// transport - console

const CONSOLE_COLOR_MAP = {
  red: (s: string) => `\x1b[31m${s}\x1b[0m`,
  green: (s: string) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s: string) => `\x1b[33m${s}\x1b[0m`,
  blue: (s: string) => `\x1b[34m${s}\x1b[0m`,
  cyan: (s: string) => `\x1b[36m${s}\x1b[0m`,
  bold: (s: string) => `\x1b[1m${s}\x1b[0m`,
};

export class LoggerTransportConsole implements LoggerTransport {
  color: keyof typeof CONSOLE_COLOR_MAP;
  constructor({
    color
  }: {
    color: keyof typeof CONSOLE_COLOR_MAP;
  }) {
    this.color = color;
  }
  printLog(key: string, ...args: Parameters<typeof console.log>) {
    const keyNice = CONSOLE_COLOR_MAP[this.color](key);
    const parts = [keyNice, ...args];
    console.log(...parts);
  }
}

// transport - file

export class LoggerTransportFile implements LoggerTransport {
  filePath: string;
  fileStream: fs.WriteStream | null = null;
  checkedIfDirExists: boolean = false;
  constructor(filePath: string) {
    this.filePath = filePath;
  }
  printLog(key: string, ...args: Parameters<typeof console.log>) {
    const parts = [key, ...args];
    const formattedMessage = nodeUtil.format(...parts) + '\n';
    this.appendLogToFileStream(formattedMessage);
  }
  private appendLogToFileStream(textLine: string) {
    // create dir if not exists
    if (!this.checkedIfDirExists) {
      this.checkedIfDirExists = true;
      const dirPath = path.dirname(this.filePath);
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
      }
    }
    // create file stream if not exists
    if (!this.fileStream) {
      this.fileStream = fs.createWriteStream(this.filePath, { flags: 'a', encoding: 'utf8' });
      this.fileStream.on('error', (err) => {
        console.error(`[LoggerTransportFile] Errore di scrittura sul file ${this.filePath}:`, err);
      });
    }
    // write to stream , that will be written to file
    this.fileStream.write(textLine);
  }
}

