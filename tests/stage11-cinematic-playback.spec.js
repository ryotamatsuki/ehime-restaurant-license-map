import {test, expect} from '@playwright/test';
import fs from 'node:fs';

test.use({video: 'on'});

async function runFullPlayback(page, testInfo, viewport, prefix) {
  test.setTimeout(135000);
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));

  await page.setViewportSize(viewport);
  await page.goto('/');
  await expect(page.locator('canvas.maplibregl-canvas')).toBeVisible({timeout: 20000});
  await page.locator('#cinematic-enter').click();
  await expect(page.locator('#cinematic-shell')).toBeVisible();

  const captureTimes = new Set([0, 5, 20, 23, 40, 50, 66, 78]);
  const telemetry = [];
  const start = Date.now();

  for (let second = 0; second <= 80; second += 1) {
    const target = start + second * 1000;
    const delay = target - Date.now();
    if (delay > 0) await page.waitForTimeout(delay);

    const sample = await page.evaluate(() => {
      const d = window.__CINEMATIC_DEBUG__ || {};
      return {
        elapsed: d.elapsed,
        month: d.month,
        beat: d.beat,
        playing: d.playing,
        camera: d.camera,
        focusPixel: d.focusPixel,
        hudRect: d.hudRect,
        seenMonthCount: d.seenMonths?.length || 0
      };
    });

    sample.second = second;
    sample.kpi = await page.locator('#cinematic-kpi').textContent();
    sample.caption = await page.locator('#cinematic-annotation').textContent();
    sample.captionVisible = await page.locator('#cinematic-annotation').evaluate(el => el.classList.contains('is-visible'));
    telemetry.push(sample);

    if (captureTimes.has(second)) {
      await page.screenshot({
        path: testInfo.outputPath(prefix + '-' + String(second).padStart(2, '0') + 's.png'),
        fullPage: true
      });
    }

    if ((second === 51 || second === 66) && viewport.width <= 760 && sample.focusPixel && sample.hudRect) {
      expect(sample.focusPixel.y).toBeLessThan(sample.hudRect.top + 8);
    }
  }

  const finalDebug = await page.evaluate(() => window.__CINEMATIC_DEBUG__);
  expect(finalDebug.seenMonths).toHaveLength(62);
  expect(finalDebug.month).toBe('2026-07');
  expect(errors).toEqual([]);

  fs.writeFileSync(
    testInfo.outputPath(prefix + '-playback-telemetry.json'),
    JSON.stringify(telemetry, null, 2)
  );
}

test('Stage 11 full 80-second desktop playback', async ({page}, testInfo) => {
  await runFullPlayback(page, testInfo, {width: 1280, height: 720}, 'desktop');
});

test('Stage 11 full 80-second mobile playback', async ({page}, testInfo) => {
  await runFullPlayback(page, testInfo, {width: 390, height: 844}, 'mobile');
});
