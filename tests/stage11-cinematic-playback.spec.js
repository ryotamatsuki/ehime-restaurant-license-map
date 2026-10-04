import {test, expect} from '@playwright/test';
import fs from 'node:fs';

test.use({video: 'on', viewport: {width: 1280, height: 720}});

test('Stage 11 full cinematic desktop playback capture', async ({page}, testInfo) => {
  test.setTimeout(125000);
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto('/');
  await expect(page.locator('canvas.maplibregl-canvas')).toBeVisible({timeout: 20000});
  await page.locator('#cinematic-enter').click();
  await expect(page.locator('#cinematic-shell')).toBeVisible();

  const samples = [];
  const captureTimes = new Set([0, 5, 22, 37, 48, 56, 70, 79]);
  const start = Date.now();

  for (let second = 0; second <= 80; second += 1) {
    const target = start + second * 1000;
    const delay = target - Date.now();
    if (delay > 0) await page.waitForTimeout(delay);

    const sample = {
      second,
      month: await page.locator('#cinematic-month').textContent(),
      evidence: await page.locator('#cinematic-evidence').textContent(),
      kpiLabel: await page.locator('#cinematic-kpi-label').textContent(),
      kpi: await page.locator('#cinematic-kpi').textContent(),
      annotation: await page.locator('#cinematic-annotation').textContent(),
      progress: await page.locator('#cinematic-progress').evaluate(el => getComputedStyle(el).width)
    };
    samples.push(sample);

    if (captureTimes.has(second)) {
      await page.screenshot({
        path: testInfo.outputPath('cinematic-' + String(second).padStart(2, '0') + 's.png'),
        fullPage: true
      });
    }
  }

  fs.writeFileSync(
    testInfo.outputPath('cinematic-playback-telemetry.json'),
    JSON.stringify(samples, null, 2)
  );
  expect(errors).toEqual([]);
});
