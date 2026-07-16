import type { EnvVarsInput } from './input-env-vars.type';

/** 
 * Environment variables for DEV.  
 */
export const INPUT_ENV_VARS_DEV: EnvVarsInput = {
  BACKEND_HTTP_API_URL: "http://localhost:8000",
  BACKEND_WS_API_URL: "ws://localhost:8000",
  APP_VERSION: "0.0.1",
  FRONTEND_APP_MODE: "DEV",
  FRONTEND_URL: "http://localhost:3000",
};