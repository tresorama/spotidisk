import { z } from 'zod';

// ========= WS =========

export const schemaWsBackendEvent = z.object({
  /** DateTime in ISO format of when the event was triggered by the backend */
  dateTimeISO: z.string(),
  payload: z.discriminatedUnion('kind', [
    z.object({
      kind: z.literal('MESSAGE'),
      text: z.string(),
      severity: z.enum([
        'INFO',
        'WARNING',
        'ERROR',
        'SUCCESS',
      ]),
    }),
    z.object({
      kind: z.literal('FRONTEND_QUERY_INVALIDATION'),
      /** Query Keys to invalidate in react-query QueryClient */
      queryKeys: z.array(z.string()),
    }),
    z.object({
      kind: z.literal('JOB_PROGRESS'),
      /** DateTime in ISO format of when the event was triggered by the backend */
      dateTimeISO: z.string(),
      jobs: z.array(z.object({
        id: z.string(),
        title: z.string(),
        executionStatus: z.enum([
          'WAITING_START',
          'RUNNING',
          'COMPLETED',
          'CANCELED',
          "ERRORED",
        ]),
        progress: z.number(),
        stepsTotal: z.number(),
        stepsCompleted: z.number(),
        messages: z.array(z.string()),
      }))
    }),
  ])
});

export type WsBackendEvent = z.infer<typeof schemaWsBackendEvent>;

