import { chromium, FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up Playwright test environment...');
  
  // Ensure required directories exist
  const directories = [
    './test-results',
    './test-results/screenshots',
    './test-results/defects',
    './test-results/videos',
    './test-results/traces'
  ];

  directories.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`📁 Created directory: ${dir}`);
    }
  });

  // Clean up old reports
  const oldReports = ['test-report.md', 'defect-report.md'];
  oldReports.forEach(report => {
    if (fs.existsSync(report)) {
      fs.unlinkSync(report);
      console.log(`🗑️  Removed old report: ${report}`);
    }
  });

  // Initialize test environment variables
  process.env.TEST_ENV = 'playwright';
  process.env.TEST_START_TIME = new Date().toISOString();

  // Browser setup for global state
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Check if the application is running
  try {
    await page.goto(config.webServer?.url || 'http://localhost:5173', {
      timeout: 30000
    });
    console.log('✅ Application is accessible');
  } catch (error) {
    console.error('❌ Application is not accessible:', error);
    throw new Error('Application is not running. Please start the application first.');
  }

  await browser.close();
  console.log('✅ Global setup completed');
}

export default globalSetup;
