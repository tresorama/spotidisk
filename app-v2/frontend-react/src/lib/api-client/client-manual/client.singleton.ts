import { CONSTANTS } from '@/constants';
import { ApiClientManual } from './lib/client';

export const apiClientManual = new ApiClientManual({
  baseUrlHttp: CONSTANTS.BACKEND_HTTP_API_URL,
  baseUrlWs: CONSTANTS.BACKEND_WS_API_URL,
});