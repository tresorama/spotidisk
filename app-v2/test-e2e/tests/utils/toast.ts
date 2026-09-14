import { type Page, expect } from '@playwright/test';

/**
 * Checker function to check for toast with expected data in page
 */
export const waitForToast = {
  /**
   * Use this if you expect an error toast for an HTTP request failed
   */
  errorHttpRequest: async ({
    page,
    httpStatusCode,
  }: {
    page: Page;
    /** HTTP status code expected */
    httpStatusCode: number;
  }) => {

    const elToast = page.locator('[data-sonner-toast]').filter({ hasText: 'API Error' }).last();
    await expect(elToast).toBeVisible();

    await expect(elToast.getByLabel('Toast Title')).toContainText('API Error');
    await expect(elToast.getByLabel('HTTP Communication Status')).toContainText('OK');
    await expect(elToast.getByLabel('HTTP Status Code')).toContainText(httpStatusCode.toString());
  },

  /**
   * Use this if you expect a success toast
   */
  success: async ({
    page,
    partialText,
  }: {
    page: Page;
    partialText: string;
  }) => {
    const elToast = page.locator('[data-sonner-toast]').filter({ hasText: partialText }).last();
    await expect(elToast).toBeVisible();
  }
};