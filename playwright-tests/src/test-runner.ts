#!/usr/bin/env node

import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

interface TestRunConfig {
  headed?: boolean;
  browser?: 'chromium' | 'firefox' | 'webkit';
  reporter?: string;
  grep?: string;
  timeout?: number;
  retries?: number;
  workers?: number;
}

class TestRunner {
  private config: TestRunConfig;
  private projectRoot: string;

  constructor(config: TestRunConfig = {}) {
    this.config = {
      headed: false,
      browser: 'chromium',
      reporter: 'line,custom-reporter',
      timeout: 30000,
      retries: 0,
      workers: undefined,
      ...config
    };
    this.projectRoot = process.cwd();
  }

  async runTests(): Promise<void> {
    console.log('🚀 Starting ExpertEase E2E Test Suite');
    console.log('=====================================\n');

    try {
      // Ensure dependencies are installed
      await this.installDependencies();
      
      // Ensure browsers are installed
      await this.installBrowsers();
      
      // Run the tests
      await this.executeTests();
      
      // Display results
      await this.displayResults();
      
    } catch (error) {
      console.error('❌ Test execution failed:', error);
      process.exit(1);
    }
  }

  private async installDependencies(): Promise<void> {
    console.log('📦 Installing dependencies...');
    
    return new Promise((resolve, reject) => {
      const npmInstall = spawn('npm', ['install'], {
        stdio: 'inherit',
        cwd: this.projectRoot
      });

      npmInstall.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Dependencies installed\n');
          resolve();
        } else {
          reject(new Error(`npm install failed with code ${code}`));
        }
      });
    });
  }

  private async installBrowsers(): Promise<void> {
    console.log('🌐 Installing Playwright browsers...');
    
    return new Promise((resolve, reject) => {
      const browserInstall = spawn('npx', ['playwright', 'install'], {
        stdio: 'inherit',
        cwd: this.projectRoot
      });

      browserInstall.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Browsers installed\n');
          resolve();
        } else {
          reject(new Error(`browser install failed with code ${code}`));
        }
      });
    });
  }

  private async executeTests(): Promise<void> {
    console.log('🧪 Running E2E tests...\n');
    
    const testCommand = this.buildTestCommand();
    
    return new Promise((resolve, reject) => {
      const testProcess = spawn('npx', testCommand, {
        stdio: 'inherit',
        cwd: this.projectRoot,
        env: {
          ...process.env,
          NODE_ENV: 'test'
        }
      });

      testProcess.on('close', (code) => {
        if (code === 0) {
          console.log('\n✅ All tests completed successfully');
          resolve();
        } else {
          console.log(`\n⚠️  Tests completed with issues (exit code: ${code})`);
          resolve(); // Don't reject, as we still want to generate reports
        }
      });

      testProcess.on('error', (error) => {
        reject(error);
      });
    });
  }

  private buildTestCommand(): string[] {
    const command = ['playwright', 'test'];
    
    if (this.config.headed) {
      command.push('--headed');
    }
    
    if (this.config.browser) {
      command.push('--project', this.config.browser);
    }
    
    if (this.config.reporter) {
      command.push('--reporter', this.config.reporter);
    }
    
    if (this.config.grep) {
      command.push('--grep', this.config.grep);
    }
    
    if (this.config.timeout) {
      command.push('--timeout', this.config.timeout.toString());
    }
    
    if (this.config.retries) {
      command.push('--retries', this.config.retries.toString());
    }
    
    if (this.config.workers !== undefined) {
      command.push('--workers', this.config.workers.toString());
    }
    
    return command;
  }

  private async displayResults(): Promise<void> {
    console.log('\n📊 Test Results Summary');
    console.log('======================\n');

    // Check if reports were generated
    const testReportPath = path.join(this.projectRoot, 'test-report.md');
    const defectReportPath = path.join(this.projectRoot, 'defect-report.md');

    if (fs.existsSync(testReportPath)) {
      console.log('📄 Test Report: test-report.md');
    }

    if (fs.existsSync(defectReportPath)) {
      console.log('🐛 Defect Report: defect-report.md');
    }

    // Check HTML report
    const htmlReportPath = path.join(this.projectRoot, 'playwright-report', 'index.html');
    if (fs.existsSync(htmlReportPath)) {
      console.log('🌐 HTML Report: playwright-report/index.html');
    }

    console.log('\n📁 Test Results Directory: test-results/');
    console.log('📁 Screenshots: test-results/screenshots/');
    console.log('📁 Defect Screenshots: test-results/defects/');
    console.log('📁 Videos: test-results/videos/');
    console.log('📁 Traces: test-results/traces/');
  }

  async runSpecificTests(pattern: string): Promise<void> {
    this.config.grep = pattern;
    await this.runTests();
  }

  async runHeadedTests(): Promise<void> {
    this.config.headed = true;
    await this.runTests();
  }

  async runSingleBrowser(browser: 'chromium' | 'firefox' | 'webkit'): Promise<void> {
    this.config.browser = browser;
    await this.runTests();
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const runner = new TestRunner();

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
ExpertEase E2E Test Runner

Usage: npm run test [options]

Options:
  --headed, -h          Run tests in headed mode (visible browser)
  --browser <name>      Run tests in specific browser (chromium, firefox, webkit)
  --grep <pattern>      Run tests matching pattern
  --timeout <ms>        Test timeout in milliseconds
  --retries <count>     Number of retries for failed tests
  --workers <count>     Number of parallel workers
  --help, -h            Show this help message

Examples:
  npm run test                           # Run all tests
  npm run test -- --headed               # Run tests in visible browser
  npm run test -- --browser firefox      # Run tests in Firefox only
  npm run test -- --grep "TC01"          # Run specific test
  npm run test -- --retries 2            # Retry failed tests 2 times
    `);
    return;
  }

  // Parse command line arguments
  const config: TestRunConfig = {};
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--headed':
      case '-h':
        config.headed = true;
        break;
      case '--browser':
        config.browser = args[++i] as 'chromium' | 'firefox' | 'webkit';
        break;
      case '--grep':
        config.grep = args[++i];
        break;
      case '--timeout':
        config.timeout = parseInt(args[++i]);
        break;
      case '--retries':
        config.retries = parseInt(args[++i]);
        break;
      case '--workers':
        config.workers = parseInt(args[++i]);
        break;
    }
  }

  const testRunner = new TestRunner(config);
  await testRunner.runTests();
}

if (require.main === module) {
  main().catch(console.error);
}

export { TestRunner, TestRunConfig };
