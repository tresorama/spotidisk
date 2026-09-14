import { CONSTANTS } from '../constants.ts';
import { utilsDisk } from '../utils/disk.ts';

async function run() {
  await deleteTestDatabase();
}

(async () => {
  try {
    console.log('Running "reset-backend" script...');
    await run();
    console.log('Success!');
    process.exit(0);
  } catch (error) {
    console.log('Error!');
    console.error(error);
    process.exit(1);
  }
})();

async function deleteTestDatabase() {
  const filePath = CONSTANTS.BACKEND_DB_FILE_PATH;
  const deleteResult = await utilsDisk.deleteFile(filePath);
  if (!deleteResult[0]) {
    console.error('Error deleting database file');
    throw new Error(deleteResult[1]);
  }
  console.log('Database deleted');
}