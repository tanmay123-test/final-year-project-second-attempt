import { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🏁 Tearing down Playwright test environment...');
  
  // Generate final summary if needed
  const testResultsPath = path.join(process.cwd(), 'test-results.json');
  if (fs.existsSync(testResultsPath)) {
    try {
      const testResults = JSON.parse(fs.readFileSync(testResultsPath, 'utf8'));
      console.log(`📊 Final test results: ${testResults.suites?.length || 0} suites executed`);
    } catch (error) {
      console.warn('⚠️  Could not parse test results:', error);
    }
  }

  // Cleanup temporary files
  const tempFiles = [
    './test-results/.tmp',
    './test-results/temp'
  ];

  tempFiles.forEach(file => {
    if (fs.existsSync(file)) {
      try {
        if (fs.statSync(file).isDirectory()) {
          fs.rmSync(file, { recursive: true, force: true });
        } else {
          fs.unlinkSync(file);
        }
        console.log(`🗑️  Cleaned up: ${file}`);
      } catch (error) {
        console.warn(`⚠️  Could not clean up ${file}:`, error);
      }
    }
  });

  // Create archive of test results if needed
  const archiveDir = `./test-results-archive-${new Date().toISOString().slice(0, 10)}`;
  if (process.env.ARCHIVE_RESULTS === 'true') {
    try {
      if (!fs.existsSync(archiveDir)) {
        fs.mkdirSync(archiveDir, { recursive: true });
      }
      // Copy important files to archive
      const filesToArchive = ['test-report.md', 'defect-report.md'];
      filesToArchive.forEach(file => {
        if (fs.existsSync(file)) {
          fs.copyFileSync(file, path.join(archiveDir, file));
        }
      });
      console.log(`📦 Results archived to: ${archiveDir}`);
    } catch (error) {
      console.warn('⚠️  Could not archive results:', error);
    }
  }

  // Print final environment info
  console.log('🌍 Test Environment Info:');
  console.log(`   OS: ${process.platform}`);
  console.log(`   Node: ${process.version}`);
  console.log(`   Test Duration: ${Date.now() - parseInt(process.env.TEST_START_TIME || '0')}ms`);
  
  console.log('✅ Global teardown completed');
}

export default globalTeardown;
