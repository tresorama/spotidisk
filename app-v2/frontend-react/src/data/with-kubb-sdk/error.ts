import axios from "axios";
import { ResponseError } from "#/lib/api-client/client-kubb-sdk/lib/generated/.kubb/client";

/** 
 * Parse various Error object into a fixed structure (`title` , `description`).  
 * Parsable types:
 * - `axios.isAxiosError`
 * - `kubb client ResponseError`
 * - `Error (native js)`
 * */
export function parseHttpRequestError(error: Error): {
  title: string,
  description: string,
} {

  if (error instanceof ResponseError) {
    return {
      title: `Request to server resulted in error (ResponseError) (HTTP ${error.status})`,
      description: JSON.stringify(error.data, null, 2),
    };
  }

  if (axios.isAxiosError(error)) {
    return {
      title: `Request to server resulted in error (axios) (HTTP ${error.status ?? "???"})`,
      description: JSON.stringify(error.toJSON(), null, 2),
    };
  }


  return {
    title: error.name,
    description: error.message,
  };

}