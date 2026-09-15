import { app as electronApp } from 'electron';

import { createConstants } from './constants';
import { createOrchestratorDeps } from './lib/orchestrator.deps';
import { Orchestrator } from './lib/orchestrator';

let ORCHESTRATOR: Orchestrator | null = null;

// `electronApp` instance is crated outsid of this code.
// Here we listen to the `electronApp.on('ready')` event and 
// create the `Orchestrator` instance, and initialize the "glue"
// between the `electronApp` and the `Orchestrator`.
electronApp.on('ready', async () => {
  // craete constants
  const CONSTANTS = await createConstants();

  // create orchestrator instance
  const orchestratorDeps = await createOrchestratorDeps({
    electronApp,
    constants: CONSTANTS,
  });
  ORCHESTRATOR = new Orchestrator({
    DEPS: orchestratorDeps,
  });

  // launch the orchestrator
  await ORCHESTRATOR.initializeElectronApp();
});
