import { preview } from 'vite';
import { chromium, expect } from '@playwright/test';
import assert from 'node:assert/strict';

function bounded(promise, label, milliseconds = 5000) {
  let timer;
  return Promise.race([promise, new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${label} deadline exceeded`)), milliseconds);
  })]).finally(() => clearTimeout(timer));
}

let server;
let browserServer;
let browser;
try {
  server = await preview({ configFile: false, preview: { host: '127.0.0.1', port: 0, strictPort: true } });
  const address = server.httpServer.address();
  assert.ok(address && typeof address === 'object');
  // The public headless probe records its actual process executable (only-shell works).
  assert.ok(process.env.ENV_CHROMIUM_EXECUTABLE, 'runner must select the recorded headless executable');
  browserServer = await chromium.launchServer({ headless: true, executablePath: process.env.ENV_CHROMIUM_EXECUTABLE, timeout: 15000 });
  browser = await chromium.connect(browserServer.wsEndpoint(), { timeout: 15000 });
  const page = await browser.newPage();
  page.setDefaultTimeout(10000);
  await page.goto(`http://127.0.0.1:${address.port}/`, { timeout: 15000 });
  await expect(page.getByRole('heading', { name: 'ENV synthetic compatibility fixture' })).toBeVisible();
  await page.getByRole('button', { name: 'Increment' }).click();
  await expect(page.getByRole('status')).toHaveText('Count 1');
  assert.equal(await page.locator('main').evaluate(element => getComputedStyle(element).paddingTop), '16px');
  await page.getByRole('link', { name: 'Details' }).click();
  await expect(page.getByRole('heading', { name: 'Synthetic details' })).toBeVisible();
  await page.reload({ timeout: 15000 });
  await expect(page.getByRole('heading', { name: 'Synthetic details' })).toBeVisible();
  console.log('Built Vite8 entry, React interaction, Tailwind padding16px and SPA navigation/reload passed in explicit Chromium');
} finally {
  try {
    if (browser) await bounded(browser.close(), 'browser disconnect');
  } finally {
    try {
      if (browserServer) {
        try { await bounded(browserServer.close(), 'browser close'); }
        catch (error) {
          await bounded(browserServer.kill(), 'browser kill');
          throw error;
        }
      }
    } finally {
      if (server) {
        server.httpServer.closeAllConnections();
        await bounded(new Promise((resolve, reject) => server.httpServer.close(error => error ? reject(error) : resolve())), 'preview close');
      }
    }
  }
}
