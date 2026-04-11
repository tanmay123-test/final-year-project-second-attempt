import { Page, TestInfo } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export class ScreenshotUtils {
  private static screenshotDir = './test-results/screenshots';
  private static defectDir = './test-results/defects';

  static ensureDirectories(): void {
    if (!fs.existsSync(this.screenshotDir)) {
      fs.mkdirSync(this.screenshotDir, { recursive: true });
    }
    if (!fs.existsSync(this.defectDir)) {
      fs.mkdirSync(this.defectDir, { recursive: true });
    }
  }

  static async captureScreenshot(
    page: Page,
    testName: string,
    testInfo: TestInfo,
    isDefect: boolean = false
  ): Promise<string> {
    this.ensureDirectories();
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${testName}_${timestamp}.png`;
    const dir = isDefect ? this.defectDir : this.screenshotDir;
    const fullPath = path.join(dir, filename);

    await page.screenshot({
      path: fullPath,
      fullPage: true
    });

    return fullPath;
  }

  static async captureDefectScreenshot(
    page: Page,
    testName: string,
    testInfo: TestInfo,
    errorElement?: string
  ): Promise<string> {
    this.ensureDirectories();
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `DEFECT_${testName}_${timestamp}.png`;
    const fullPath = path.join(this.defectDir, filename);

    if (errorElement) {
      try {
        const element = page.locator(errorElement);
        await element.scrollIntoViewIfNeeded();
        
        // Highlight the error element
        await element.evaluate((el: HTMLElement) => {
          el.style.border = '3px solid red';
          el.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
        });

        await page.screenshot({
          path: fullPath,
          fullPage: true
        });

        // Remove highlight
        await element.evaluate((el: HTMLElement) => {
          el.style.border = '';
          el.style.backgroundColor = '';
        });
      } catch (e) {
        // Fallback to full page screenshot if element not found
        await page.screenshot({
          path: fullPath,
          fullPage: true
        });
      }
    } else {
      await page.screenshot({
        path: fullPath,
        fullPage: true
      });
    }

    return fullPath;
  }
}

export class TestUtils {
  static generateTestCaseId(module: string, index: number): string {
    const moduleCode = module.toUpperCase().substring(0, 2);
    return `TC${moduleCode}${String(index).padStart(2, '0')}`;
  }

  static formatDuration(ms: number): string {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  }

  static sanitizeString(str: string): string {
    return str.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, '_');
  }

  static async waitForPageLoad(page: Page, timeout: number = 10000): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  }

  static async takeScreenshotOnFailure(
    page: Page,
    testName: string,
    testInfo: TestInfo,
    error?: Error
  ): Promise<string> {
    const screenshotPath = await ScreenshotUtils.captureDefectScreenshot(
      page,
      testName,
      testInfo
    );
    
    console.log(`📸 Defect screenshot captured: ${screenshotPath}`);
    return screenshotPath;
  }
}

export class TestDataGenerator {
  static generateTestUser(): any {
    const timestamp = Date.now();
    return {
      username: `testuser_${timestamp}`,
      email: `test_${timestamp}@example.com`,
      password: 'Test@123456',
      fullName: `Test User ${timestamp}`,
      phone: `9876543${timestamp.toString().slice(-4)}`
    };
  }

  static generateRandomText(length: number = 10): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }
}
