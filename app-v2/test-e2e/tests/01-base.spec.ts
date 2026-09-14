import { test, expect } from '@playwright/test';
import { CONSTANTS } from '../constants';

const { FRONTEND_URL } = CONSTANTS;

test.use({
  baseURL: FRONTEND_URL,
});

test('open / and check <title>', async ({ page }) => {
  // go to /
  await page.goto('/');

  // check <title>
  await expect(page).toHaveTitle('SpotiDisk');
});

test('open app and check ws connection status - should be connected', async ({ page }) => {
  // go to /
  await page.goto('/');

  // check DOM
  const elGlobalWsConnectionStatus = page.getByLabel('Global WS Connection Status');
  await expect(elGlobalWsConnectionStatus).toContainText('Connected');
  await expect(elGlobalWsConnectionStatus).toHaveAttribute('data-status', 'connected');
});

test('open app and navigate to /add-playlist', async ({ page }) => {
  // go to /
  await page.goto('/');

  // got to /add-playlist page by clicking button
  await page
    .getByLabel('Sidebar Footer')
    .getByRole('button', { name: 'Add Playlist' })
    .click();
  await page.waitForURL(`**/add-playlist`);

  // check heading
  const elH1 = page.getByRole('heading', { level: 1, name: 'Add playlist', exact: true });
  await expect(elH1).toBeVisible();
});

test('open app and navigate to /settings', async ({ page }) => {
  // go to /
  await page.goto('/');

  // got to /settings page by clicking button
  await page
    .getByLabel('Sidebar Footer')
    .getByRole('button', { name: 'Settings' })
    .click();
  await page.waitForURL(`**/settings`);

  // check heading
  const elH1 = page.getByRole('heading', { level: 1, name: 'Settings', exact: true });
  await expect(elH1).toBeVisible();
});

