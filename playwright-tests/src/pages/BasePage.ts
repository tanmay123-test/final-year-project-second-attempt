import { Page, Locator } from '@playwright/test';
import { ScreenshotUtils, TestUtils } from '../utils/helpers';

export abstract class BasePage {
  protected page: Page;
  protected url: string;

  constructor(page: Page, url: string) {
    this.page = page;
    this.url = url;
  }

  async navigate(): Promise<void> {
    await this.page.goto(this.url);
    await TestUtils.waitForPageLoad(this.page);
  }

  async waitForElement(selector: string, timeout: number = 10000): Promise<Locator> {
    return this.page.waitForSelector(selector, { timeout });
  }

  async clickElement(selector: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.click(selector);
  }

  async fillInput(selector: string, value: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.fill(selector, value);
  }

  async getText(selector: string): Promise<string> {
    await this.waitForElement(selector);
    return await this.page.textContent(selector) || '';
  }

  async isVisible(selector: string): Promise<boolean> {
    try {
      await this.waitForElement(selector, 5000);
      return await this.page.isVisible(selector);
    } catch {
      return false;
    }
  }

  async waitForNavigation(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async takeScreenshot(testName: string, testInfo: any, isDefect: boolean = false): Promise<string> {
    return await ScreenshotUtils.captureScreenshot(this.page, testName, testInfo, isDefect);
  }

  async takeDefectScreenshot(testName: string, testInfo: any, errorElement?: string): Promise<string> {
    return await ScreenshotUtils.captureDefectScreenshot(this.page, testName, testInfo, errorElement);
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  async waitForURL(expectedURL: string, timeout: number = 10000): Promise<void> {
    await this.page.waitForURL(expectedURL, { timeout });
  }

  async pressKey(key: string): Promise<void> {
    await this.page.keyboard.press(key);
  }

  async scrollIntoView(selector: string): Promise<void> {
    const element = this.page.locator(selector);
    await element.scrollIntoViewIfNeeded();
  }

  async hover(selector: string): Promise<void> {
    await this.page.hover(selector);
  }

  async selectOption(selector: string, value: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.selectOption(selector, value);
  }

  async checkCheckbox(selector: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.check(selector);
  }

  async uncheckCheckbox(selector: string): Promise<void> {
    await this.waitForElement(selector);
    await this.page.uncheck(selector);
  }

  async isElementEnabled(selector: string): Promise<boolean> {
    await this.waitForElement(selector);
    return await this.page.isEnabled(selector);
  }

  async waitForElementToDisappear(selector: string, timeout: number = 10000): Promise<void> {
    await this.page.waitForSelector(selector, { state: 'detached', timeout });
  }
}
