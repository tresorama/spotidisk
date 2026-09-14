# test-end-to-end of spotidisk app

Project for running end-to-end tests of the app with Playwright (typescript).

## First Time Setup

```bash
# install dependencies
pnpm i
# install browsers of Playwright
pnpm playwright:browsers:install
```

## Run Test in UI Mode

In ui mode, tests must be manually triggered in the UI.  
This mode allow to easy debug.

```bash
pnpm test:ui
```

## Run Test in Headed Mode

In headed mode, tests are run in a browser with GUI but without human interaction.

```bash
pnpm test:headed
```