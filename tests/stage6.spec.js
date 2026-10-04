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
