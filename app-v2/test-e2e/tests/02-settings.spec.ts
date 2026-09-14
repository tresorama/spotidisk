import { test, expect } from '@playwright/test';
import { CONSTANTS } from '../constants';
import { API_ENDPOINTS, checkHttpResponseState, isThisHttpResponse } from './utils/api-calls';
import { waitForToast } from './utils/toast';

const { FRONTEND_URL } = CONSTANTS;

// init tests

test.use({
  baseURL: FRONTEND_URL,
});

// run tests

test.describe.serial('Settings lifecycle', () => {

  test('go to /settings and check initial settings values', async ({ page }) => {
    const API_CALL = API_ENDPOINTS.SETTINGS_GET_SETTINGS();

    // go to /settings
    // listen response
    const [response] = await Promise.all([
      page.waitForResponse(isThisHttpResponse(API_CALL)),
      page.goto('/settings'),
    ]);

    // check request result - network
    await checkHttpResponseState({
      response,
      resStatusCode: API_CALL.RES_OK_STATUS,
    });

    // check request result - DOM

    const elSettingsReadonly = page.getByLabel('Settings Readonly');
    const elSettingsMutable = page.getByLabel('Settings Mutable', { exact: true });
    await expect(elSettingsReadonly).toBeVisible();
    await expect(elSettingsMutable).toBeVisible();

    const data = {
      readonly: {
        user_config_file_path: await elSettingsReadonly.getByRole('textbox', { name: 'User config file path' }).inputValue(),
        binary_deno_file_path: await elSettingsReadonly.getByRole('textbox', { name: 'Binary deno file path' }).inputValue(),
        binary_ffmpeg_file_path: await elSettingsReadonly.getByRole('textbox', { name: 'Binary ffmpeg file path' }).inputValue(),
      },
      mutable: {
        download_folder: await elSettingsMutable.getByRole('textbox', { name: 'Download Folder' }).inputValue(),
        file_name_pattern: await elSettingsMutable.getByRole('textbox', { name: 'File Name Pattern' }).inputValue(),
      }
    };
    // console.log({ data });
    expect(data.readonly.user_config_file_path).toMatch(/config_test_e2e.json/);
    expect(data.readonly.binary_deno_file_path).toMatch(/deno/);
    expect(data.readonly.binary_ffmpeg_file_path).toMatch(/ffmpeg/);

    expect(data.mutable.download_folder).toMatch(/Desktop\/Spotidisk/);
    expect(data.mutable.file_name_pattern).toBe("{index} {title} - {artist}");

  });

  test('click SETTINGS_READONLY action REVEAL', async ({ page }) => {
    const API_CALL = API_ENDPOINTS.UTILS_DISK_REVEAL_PATH();

    // go to /settings
    await page.goto('/settings');

    // trigger action
    const [response] = await Promise.all([
      page.waitForResponse(isThisHttpResponse(API_CALL)),
      page
        .getByLabel('Settings Readonly')
        .getByRole('button', { name: 'Reveal' })
        .click(),
    ]);

    // check request result - network
    await checkHttpResponseState({
      response,
      resStatusCode: API_CALL.RES_OK_STATUS,
    });

    // check request result - DOM

    await waitForToast.success({ page, partialText: API_CALL.RES_OK_TOAST_MSG });

  });

  test('update SETTINGS_MUTABLE and chck result', async ({ page }) => {
    const API_CALL_FORM_SUBMIT = API_ENDPOINTS.SETTINGS_UPDATE_SETTINGS();
    const API_CALL_GET_SETTINGS = API_ENDPOINTS.SETTINGS_GET_SETTINGS();

    // go to /settings
    await page.goto('/settings');

    // get form els
    const elForm = page.getByRole('form', { name: 'Form - Update Settings Mutable' });
    const elInputDownloadFolder = elForm.getByRole('textbox', { name: 'Download Folder' });
    const elInputFileNamePattern = elForm.getByRole('textbox', { name: 'File Name Pattern' });
    const elButtonSubmit = elForm.getByRole('button', { name: 'Submit' });
    await expect(elForm).toBeVisible();
    await expect(elInputDownloadFolder).toBeVisible();
    await expect(elInputFileNamePattern).toBeVisible();
    await expect(elButtonSubmit).toBeVisible();

    // get currnt state + prepare new state
    const OLD_DOWNLOAD_FOLDER = await elInputDownloadFolder.inputValue();
    const OLD_FILE_NAME_PATTERN = await elInputFileNamePattern.inputValue();
    const NEW_DOWNLOAD_FOLDER = `${OLD_DOWNLOAD_FOLDER}_updated`;
    const NEW_FILE_NAME_PATTERN = `${OLD_FILE_NAME_PATTERN} updated`;

    // fill form
    await elInputDownloadFolder.fill(NEW_DOWNLOAD_FOLDER);
    await elInputFileNamePattern.fill(NEW_FILE_NAME_PATTERN);

    // submit form
    const [
      responseGetSettings,
      responseFormSubmit
    ] = await Promise.all([
      page.waitForResponse(isThisHttpResponse(API_CALL_GET_SETTINGS)),
      page.waitForResponse(isThisHttpResponse(API_CALL_FORM_SUBMIT)),
      elButtonSubmit.click(),
    ]);

    // check request result - network
    await checkHttpResponseState({
      response: responseFormSubmit,
      resStatusCode: API_CALL_FORM_SUBMIT.RES_OK_STATUS,
    });
    await checkHttpResponseState({
      response: responseGetSettings,
      resStatusCode: API_CALL_GET_SETTINGS.RES_OK_STATUS,
    });

    // check request result - DOM

    await waitForToast.success({ page, partialText: API_CALL_FORM_SUBMIT.RES_OK_TOAST_MSG });

    await expect(elInputDownloadFolder).toHaveValue(NEW_DOWNLOAD_FOLDER, { timeout: 20 * 1000 });
    await expect(elInputFileNamePattern).toHaveValue(NEW_FILE_NAME_PATTERN, { timeout: 20 * 1000 });

  });

});
