import * as fs from 'node:fs/promises';

export const utilsDisk = {
  deleteFile: async (filePath: string) => {
    try {
      await fs.unlink(filePath);
      return [true, "DELETED"] as const;
    } catch (error) {
      const isFileNotFoundError = error instanceof Error && 'code' in error && error.code === 'ENOENT';
      if (isFileNotFoundError) {
        return [true, "FILE_NOT_FOUND"] as const;
      }
      console.error(error);
      return [false, "FILE_DELETE_ERROR"] as const;
    }
  }
};