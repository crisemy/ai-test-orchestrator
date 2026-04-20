const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  reporter: [['html', { outputFolder: 'reports/html-report', open: 'never' }]],
  // ...existing configuration
});