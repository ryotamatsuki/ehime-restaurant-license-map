import {defineConfig} from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 45000,
  retries: 1,
  // WebGL suites share the CI GPU; validate a normal single-view playback.
  // Keep every rendered-month assertion, without competing GIS browser tabs.
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:4173',
    trace: 'retain-on-failure'
  },
  webServer: {
    command: 'npm run preview:web -- --port 4173',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: false,
    timeout: 60000
  }
});
