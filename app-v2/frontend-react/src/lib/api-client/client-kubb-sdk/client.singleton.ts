import { CONSTANTS } from '@/constants';
import { ApiClientKubbSdk } from './lib/client';

export const apiClientKubbSdk = new ApiClientKubbSdk({
  baseUrlHttp: CONSTANTS.BACKEND_HTTP_API_URL,
  baseUrlWs: CONSTANTS.BACKEND_WS_API_URL,
});