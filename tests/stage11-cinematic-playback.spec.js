import {test, expect} from '@playwright/test';
import fs from 'node:fs';

test.use({video: 'on'});

async function runFullPlayback(page, testInfo, viewport, prefix) {
  test.setTimeout(180000);
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error' && /shader|WebGL|deck.gl|NaN/i.test(message.text())) errors.push(message.text());
  });

  await page.setViewportSize(viewport);
  await page.goto('/');
  await expect(page.locator('canvas.maplibregl-canvas')).toBeVisible({timeout: 20000});
  await page.locator('#cinematic-enter').click();
  await expect(page.locator('#cinematic-shell')).toBeVisible();

  const captureTimes = new Set([0, 40, 78]);
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
        seenMonthCount: d.seenMonths?.length || 0,
        kpi: document.querySelector('#cinematic-kpi').textContent,
        kpiVisible: document.querySelector('#cinematic-kpi-wrap').classList.contains('is-visible'),
        place: document.querySelector('#cinematic-place').textContent,
        scope: document.querySelector('#cinematic-scope').textContent,
        supportVisible: document.querySelector('#cinematic-support').classList.contains('is-visible'),
        chartVisible: document.querySelector('#cinematic-chart').classList.contains('is-visible'),
        caption: document.querySelector('#cinematic-annotation').textContent,
        captionVisible: document.querySelector('#cinematic-annotation').classList.contains('is-visible')
      };
    });

    sample.second = second;
    telemetry.push(sample);

    if (sample.elapsed >= 61.5 && sample.elapsed <= 63.25) {
      expect(sample.kpi).toBe('158件');
      expect(sample.place).toBe('松山市全体');
      expect(sample.scope).toBe('松山市全体');
      expect(sample.supportVisible).toBe(true);
      expect(sample.chartVisible).toBe(false);
    }
    if (sample.elapsed >= 64.55 && sample.elapsed <= 69.0) {
      expect(sample.kpi).toBe('14件');
      expect(sample.place).toBe('道後');
      expect(sample.scope).toBe('道後周辺の1km区画・高精度地点');
      expect(sample.chartVisible).toBe(true);
    }

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

  expect(await page.evaluate(() => document.documentElement.scrollHeight)).toBeLessThanOrEqual(viewport.height);
  const finalDebug = await page.evaluate(() => window.__CINEMATIC_DEBUG__);
  fs.writeFileSync(testInfo.outputPath(prefix + '-final-playback-telemetry.json'), JSON.stringify({finalDebug, telemetry}, null, 2));
  expect(finalDebug.seenMonths).toHaveLength(62);
  expect(finalDebug.month).toBe('2026-07');
  expect(errors).toEqual([]);

  fs.writeFileSync(
    testInfo.outputPath(prefix + '-playback-telemetry.json'),
    JSON.stringify(telemetry, null, 2)
  );

  // Wall-clock sampling can be late while CI captures screenshots. Verify the
  // exact film-clock frames separately after the uninterrupted 80-second run.
  for (const second of [2, 25, 40, 51, 62, 66, 78]) {
    await page.evaluate(t => window.__CINEMATIC_TEST_API__.seek(t), second);
    if (second === 62 || second === 66) {
    await expect(page.locator('#cinematic-kpi')).toHaveText(second === 62 ? '158件' : '14件');
    await expect(page.locator('#cinematic-place')).toHaveText(second === 62 ? '松山市全体' : '道後');
    await expect(page.locator('#cinematic-scope')).toHaveText(
      second === 62 ? '松山市全体' : '道後周辺の1km区画・高精度地点'
    );
    if (second === 62) {
      await expect(page.locator('#cinematic-support')).toHaveText('位置を特定した48件を地図に表示');
      await expect(page.locator('#cinematic-chart')).not.toHaveClass(/is-visible/);
    } else {
      await expect(page.locator('#cinematic-chart')).toHaveClass(/is-visible/);
    }
    }
    if (second === 51) {
      await expect.poll(async () => (await page.evaluate(() => window.__CINEMATIC_TEST_API__.basemap())).coast).toBeGreaterThan(0);
      await expect(page.locator('#cinematic-chart svg')).toHaveAttribute('aria-label', '2025-05 1件、2025-06 0件、2025-07 0件、2025-08 5件');
    }
    if (second === 66) await expect.poll(async () => (await page.evaluate(() => window.__CINEMATIC_TEST_API__.basemap())).roads).toBeGreaterThan(0);
    await page.screenshot({path: testInfo.outputPath(prefix + '-' + second + 's.png'), fullPage: true, animations: 'disabled'});
  }
}

test('Stage 11 full 80-second desktop playback', async ({page}, testInfo) => {
  await runFullPlayback(page, testInfo, {width: 1280, height: 720}, 'desktop');
});

test('Stage 11 full 80-second mobile playback', async ({page}, testInfo) => {
  await runFullPlayback(page, testInfo, {width: 390, height: 844}, 'mobile');
});

