import {test, expect} from '@playwright/test';

test('desktop time-map controls and views work', async ({page}) => {
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));

  await page.setViewportSize({width: 1440, height: 900});
  await page.goto('/');
  await expect(page.locator('h1')).toContainText('Ehime Restaurant License Map');
  await expect(page.locator('canvas.maplibregl-canvas')).toBeVisible({timeout: 20000});
  await expect(page.locator('#coverage-badge')).toContainText('完全観測');
  await expect(page.locator('#municipality-select')).toHaveValue('382019');
  await expect(page.locator('#business-select')).toHaveValue('飲食店営業');
  await expect(page.locator('#retrospective-toggle')).toBeChecked();
  await expect(page.locator('#timeline-start')).toHaveText('2021-06');

  const hybridSlider = page.locator('#month-slider');
  expect(Number(await hybridSlider.getAttribute('max'))).toBe(61);
  await hybridSlider.fill('0');
  await expect(page.locator('#timeline-current')).toHaveText('2021-06');
  await expect(page.locator('#coverage-badge')).toContainText('参考復元');
  await expect(page.locator('#metric-total-label')).toContainText('参考復元');
  await expect(page.locator('button[data-view="mesh1"]')).toBeDisabled();

  await hybridSlider.fill('61');
  await expect(page.locator('#timeline-current')).toHaveText('2026-07');
  await expect(page.locator('#coverage-badge')).toContainText('完全観測');

  await page.locator('button[data-view="heatmap"]').click();
  await expect(page.locator('button[data-view="heatmap"]')).toHaveClass(/active/);

  await page.locator('button[data-view="hexagon"]').click();
  await expect(page.locator('button[data-view="hexagon"]')).toHaveClass(/active/);

  await page.locator('button[data-view="mesh1"]').click();
  await expect(page.locator('button[data-view="mesh1"]')).toHaveClass(/active/);
  await expect(page.locator('#metric-third')).not.toHaveText('—');

  await page.locator('button[data-period="rolling12"]').click();
  await expect(page.locator('button[data-period="rolling12"]')).toHaveClass(/active/);
  await expect(page.locator('#coverage-badge')).toContainText('12か月');

  const slider = page.locator('#month-slider');
  const max = Number(await slider.getAttribute('max'));
  expect(max).toBeGreaterThan(0);
  await slider.fill('0');
  await expect(page.locator('#timeline-current')).not.toHaveText('—');

  expect(pageErrors).toEqual([]);
});

test('mobile layout remains usable', async ({page}) => {
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));

  await page.setViewportSize({width: 390, height: 844});
  await page.goto('/');
  await expect(page.locator('canvas.maplibregl-canvas')).toBeVisible({timeout: 20000});
  await expect(page.locator('.panel')).toBeVisible();
  await expect(page.locator('#municipality-select')).toBeVisible();
  await expect(page.locator('#month-slider')).toBeVisible();

  await page.locator('button[data-view="points"]').click();
  await page.locator('#play-button').click();
  await page.waitForTimeout(1200);
  await page.locator('#play-button').click();

  await expect(page.locator('#timeline-current')).not.toHaveText('—');
  expect(pageErrors).toEqual([]);
});



test('cinematic mode stages local/citywide KPIs and hands off to Explore', async ({page}) => {
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));
  await page.setViewportSize({width: 1440, height: 900});
  await page.goto('/');
  await expect(page.locator('canvas.maplibregl-canvas')).toBeVisible({timeout: 20000});

  await page.locator('#cinematic-enter').click();
  await expect(page.locator('#cinematic-shell')).toBeVisible();
  await expect(page.locator('#cinematic-month')).toHaveText('2021.06');
  await expect(page.locator('#cinematic-evidence')).toContainText('参考復元');

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(40));
  await expect(page.locator('#cinematic-month')).toHaveText('2025.05');
  await expect(page.locator('#cinematic-kpi')).toHaveText('165件');
  await expect(page.locator('#cinematic-scope')).toHaveText('松山市全体');
  await expect(page.locator('#cinematic-annotation')).toContainText('市内に広がる');

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(50.6));
  await expect(page.locator('#cinematic-month')).toHaveText('2025.08');
  await expect(page.locator('#cinematic-kpi')).toHaveText('5件');
  await expect(page.locator('#cinematic-scope')).toContainText('1km区画');
  await expect(page.locator('#cinematic-chart')).toHaveClass(/is-visible/);

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(62));
  await expect(page.locator('#cinematic-month')).toHaveText('2026.02');
  await expect(page.locator('#cinematic-kpi')).toHaveText('158件');
  await expect(page.locator('#cinematic-kpi-label')).toHaveText('松山市全体');
  await expect(page.locator('#cinematic-place')).toHaveText('松山市全体');
  await expect(page.locator('#cinematic-scope')).toHaveText('松山市全体');
  await expect(page.locator('#cinematic-support')).toHaveText('位置を特定した48件を地図に表示');
  await expect(page.locator('#cinematic-chart')).not.toHaveClass(/is-visible/);

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(64));
  await expect(page.locator('#cinematic-kpi-wrap')).not.toHaveClass(/is-visible/);
  await expect(page.locator('#cinematic-chart')).not.toHaveClass(/is-visible/);

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(66));
  await expect(page.locator('#cinematic-month')).toHaveText('2026.02');
  await expect(page.locator('#cinematic-kpi')).toHaveText('14件');
  await expect(page.locator('#cinematic-place')).toHaveText('道後');
  await expect(page.locator('#cinematic-scope')).toHaveText('道後周辺の1km区画・高精度地点');
  await expect(page.locator('#cinematic-support')).not.toHaveClass(/is-visible/);
  await expect(page.locator('#cinematic-chart')).toHaveClass(/is-visible/);
  await expect(page.locator('#cinematic-annotation')).toContainText('道後の同じ区画に、14件');

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(78));
  await expect(page.locator('#cinematic-month')).toHaveText('2026.07');
  await expect(page.locator('#cinematic-final')).toHaveClass(/is-visible/);
  await expect(page.locator('#cinematic-closing-stats')).toContainText('道後 19/23か月');
  await expect(page.locator('#cinematic-closing-stats')).toContainText('三津 15/23か月');

  await page.locator('#cinematic-target-mitsu').click();
  await expect(page.locator('#cinematic-explore')).toContainText('三津');
  await page.locator('#cinematic-explore').click();

  await expect(page.locator('#cinematic-shell')).toBeHidden();
  await expect(page.locator('#timeline-current')).toHaveText('2025-08');
  await expect(page.locator('.panel')).toBeVisible();
  expect(pageErrors).toEqual([]);
});

test('cinematic pause freezes clock and camera, then resume continues', async ({page}) => {
  await page.setViewportSize({width: 1280, height: 720});
  await page.goto('/');
  await page.locator('#cinematic-enter').click();
  await page.waitForTimeout(1500);
  await page.locator('#cinematic-play').click();

  const before = await page.evaluate(() => window.__CINEMATIC_DEBUG__);
  await page.waitForTimeout(1200);
  const after = await page.evaluate(() => window.__CINEMATIC_DEBUG__);

  expect(Math.abs(after.elapsed - before.elapsed)).toBeLessThan(0.03);
  expect(after.camera.lon).toBeCloseTo(before.camera.lon, 6);
  expect(after.camera.lat).toBeCloseTo(before.camera.lat, 6);
  expect(after.camera.zoom).toBeCloseTo(before.camera.zoom, 6);

  await page.locator('#cinematic-play').click();
  await page.waitForTimeout(700);
  const resumed = await page.evaluate(() => window.__CINEMATIC_DEBUG__);
  expect(resumed.elapsed).toBeGreaterThan(after.elapsed + 0.5);
});

test('cinematic interpolates intermediate camera keyframes', async ({page}) => {
  await page.setViewportSize({width: 1280, height: 720});
  await page.goto('/');
  await page.locator('#cinematic-enter').click();

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(46.6));
  const pulled = await page.evaluate(() => window.__CINEMATIC_DEBUG__.camera);
  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(47.4));
  const moving = await page.evaluate(() => window.__CINEMATIC_DEBUG__.camera);
  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(49.0));
  const settled = await page.evaluate(() => window.__CINEMATIC_DEBUG__.camera);

  expect(pulled.zoom).toBeLessThan(11);
  expect(moving.lon).toBeLessThan(pulled.lon);
  expect(settled.lon).toBeLessThan(moving.lon);
  expect(settled.zoom).toBeGreaterThan(12);
});

test('cinematic mobile reduced-motion retains the same information', async ({page}) => {
  await page.emulateMedia({reducedMotion: 'reduce'});
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('/');
  await page.locator('#cinematic-enter').click();

  await expect(page.locator('#cinematic-shell')).toBeVisible();
  await expect(page.locator('#cinematic-play')).toHaveText('▶');

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(50.6));
  let debug = await page.evaluate(() => window.__CINEMATIC_DEBUG__);
  expect(debug.focusPixel.y).toBeLessThan(debug.hudRect.top + 8);

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(62));
  await expect(page.locator('#cinematic-kpi')).toHaveText('158件');
  await expect(page.locator('#cinematic-place')).toHaveText('松山市全体');
  await expect(page.locator('#cinematic-scope')).toHaveText('松山市全体');
  await expect(page.locator('#cinematic-support')).toHaveText('位置を特定した48件を地図に表示');
  await expect(page.locator('#cinematic-chart')).not.toHaveClass(/is-visible/);

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(66));
  await expect(page.locator('#cinematic-kpi')).toHaveText('14件');
  await expect(page.locator('#cinematic-scope')).toContainText('高精度地点');

  debug = await page.evaluate(() => window.__CINEMATIC_DEBUG__);
  expect(debug.reduced).toBe(true);
  expect(debug.camera.pitch).toBeLessThanOrEqual(12);
  expect(debug.focusPixel.y).toBeLessThan(debug.hudRect.top + 8);

  await page.evaluate(() => window.__CINEMATIC_TEST_API__.seek(78));
  await expect(page.locator('#cinematic-final')).toHaveClass(/is-visible/);
  await page.locator('#cinematic-exit').click();
  await expect(page.locator('#cinematic-shell')).toBeHidden();
});

