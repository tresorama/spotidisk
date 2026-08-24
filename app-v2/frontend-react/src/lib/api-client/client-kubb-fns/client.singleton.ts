import { CONSTANTS } from '@/constants';
import { ApiClientKubbFns } from './lib/client';

export const apiClientKubbFns = new ApiClientKubbFns({
  baseUrlHttp: CONSTANTS.BACKEND_HTTP_API_URL,
  baseUrlWs: CONSTANTS.BACKEND_WS_API_URL,
});