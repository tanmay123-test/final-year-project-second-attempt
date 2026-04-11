import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  // Selectors - Updated to match actual frontend structure
  private readonly serviceSelection = '.service-selection-page';
  private readonly healthcareService = 'button:has-text("Healthcare")';
  private readonly freelanceService = 'button:has-text("Freelance")';
  private readonly carService = 'button:has-text("Car")';
  private readonly housekeepingService = 'button:has-text("Housekeeping")';
  private readonly moneyService = 'button:has-text("Finny")';
  private readonly navigationMenu = 'nav';
  private readonly userMenu = '[data-testid="user-menu"]';
  private readonly loginButton = 'a:has-text("login"), button:has-text("Login")';
  private readonly signupButton = 'a:has-text("signup"), button:has-text("Signup")';

  constructor(page: Page) {
    super(page, '/');
  }

  async navigateToHome(): Promise<void> {
    await this.navigate();
  }

  async isHomePageLoaded(): Promise<boolean> {
    return await this.isVisible(this.serviceSelection);
  }

  async selectHealthcareService(): Promise<void> {
    await this.clickElement(this.healthcareService);
    await this.waitForNavigation();
  }

  async selectFreelanceService(): Promise<void> {
    await this.clickElement(this.freelanceService);
    await this.waitForNavigation();
  }

  async selectCarService(): Promise<void> {
    await this.clickElement(this.carService);
    await this.waitForNavigation();
  }

  async selectHousekeepingService(): Promise<void> {
    await this.clickElement(this.housekeepingService);
    await this.waitForNavigation();
  }

  async selectMoneyService(): Promise<void> {
    await this.clickElement(this.moneyService);
    await this.waitForNavigation();
  }

  async clickLoginButton(): Promise<void> {
    await this.clickElement(this.loginButton);
  }

  async clickSignupButton(): Promise<void> {
    await this.clickElement(this.signupButton);
  }

  async isNavigationMenuVisible(): Promise<boolean> {
    return await this.isVisible(this.navigationMenu);
  }

  async isUserMenuVisible(): Promise<boolean> {
    return await this.isVisible(this.userMenu);
  }

  async getServiceCount(): Promise<number> {
    const services = await this.page.locator('.service-card').count();
    return services;
  }
}
