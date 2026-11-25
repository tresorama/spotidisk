import { toast } from "./sonner";

/**
* Sonner, (toast library) if a lot of `toast()` call are called in a short amount of time
* causes memory problem and can freeze the browser tab.
* 
* We introduce a Queue layer to avoid overloading sonner
*/


/** A simple Queue of functions as items */
function createFnQueue<TFn extends () => void>(
  options: {
    intervalInMs: number,
  }
) {

  // the queue use window.setIntrval so can be created only on browser
  if (typeof window === "undefined") return null;

  // state
  let interval: number | undefined = undefined;
  const queue: TFn[] = [];

  // public api
  return {
    enqueueItem: (fn: TFn) => {
      queue.push(fn);
    },
    init: () => {
      function tick() {
        const item = queue.shift();
        if (!item) return;
        item();
      }

      interval = window.setInterval(tick, options.intervalInMs);
      window.addEventListener('beforeunload', () => {
        window.clearInterval(interval);
      });
    },
  };

}

// init the queu globally only on browser
const toastQueueApi = createFnQueue({ intervalInMs: 50 });
toastQueueApi?.init();

/** `toast` api that uses the queue layer to throttled  */
export const toastThrottled: {
  message: (...args: Parameters<typeof toast.message>) => void,
  warning: (...args: Parameters<typeof toast.warning>) => void,
  error: (...args: Parameters<typeof toast.error>) => void,
  success: (...args: Parameters<typeof toast.success>) => void,
} = {
  message: (...args) => toastQueueApi?.enqueueItem(() => toast.message(...args)),
  warning: (...args) => toastQueueApi?.enqueueItem(() => toast.warning(...args)),
  error: (...args) => toastQueueApi?.enqueueItem(() => toast.error(...args)),
  success: (...args) => toastQueueApi?.enqueueItem(() => toast.success(...args)),
};

