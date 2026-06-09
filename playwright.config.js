const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  testMatch: ['**/*.spec.ts', '**/*.spec.tsx'],
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'npx http-server ui-testing-lab -p 3000 --silent',
    port: 3000,
    cwd: '.',
    reuseExistingServer: true,
  },
  reporter: [['html', { outputFolder: 'reports/html-report', open: 'never' }]],
});
