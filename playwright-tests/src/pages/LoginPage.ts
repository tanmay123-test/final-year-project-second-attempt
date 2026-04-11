import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  // Selectors
  private readonly emailInput = '[data-testid="email-input"]';
  private readonly passwordInput = '[data-testid="password-input"]';
  private readonly loginButton = '[data-testid="login-submit"]';
  private readonly errorMessage = '[data-testid="error-message"]';
  private readonly forgotPasswordLink = '[data-testid="forgot-password"]';
  private readonly signupLink = '[data-testid="signup-link"]';
  private readonly rememberMeCheckbox = '[data-testid="remember-me"]';

  constructor(page: Page) {
    super(page, '/login');
  }

  async navigateToLogin(): Promise<void> {
    await this.navigate();
  }

  async enterEmail(email: string): Promise<void> {
    await this.fillInput(this.emailInput, email);
  }

  async enterPassword(password: string): Promise<void> {
    await this.fillInput(this.passwordInput, password);
  }

  async clickLoginButton(): Promise<void> {
    await this.clickElement(this.loginButton);
    await this.waitForNavigation();
  }

  async login(email: string, password: string): Promise<void> {
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.clickLoginButton();
  }

  async getErrorMessage(): Promise<string> {
    return await this.getText(this.errorMessage);
  }

  async isErrorMessageVisible(): Promise<boolean> {
    return await this.isVisible(this.errorMessage);
  }

  async isForgotPasswordLinkVisible(): Promise<boolean> {
    return await this.isVisible(this.forgotPasswordLink);
  }

  async isSignupLinkVisible(): Promise<boolean> {
    return await this.isVisible(this.signupLink);
  }

  async clickForgotPassword(): Promise<void> {
    await this.clickElement(this.forgotPasswordLink);
  }

  async clickSignupLink(): Promise<void> {
    await this.clickElement(this.signupLink);
  }

  async checkRememberMe(): Promise<void> {
    await this.checkCheckbox(this.rememberMeCheckbox);
  }

  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.isElementEnabled(this.loginButton);
  }

  async waitForLoginSuccess(): Promise<void> {
    await this.page.waitForURL(/dashboard|home/, { timeout: 10000 });
  }
}
