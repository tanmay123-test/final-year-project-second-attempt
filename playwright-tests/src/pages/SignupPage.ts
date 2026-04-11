import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class SignupPage extends BasePage {
  // Selectors
  private readonly fullNameInput = '[data-testid="fullname-input"]';
  private readonly emailInput = '[data-testid="email-input"]';
  private readonly phoneInput = '[data-testid="phone-input"]';
  private readonly passwordInput = '[data-testid="password-input"]';
  private readonly confirmPasswordInput = '[data-testid="confirm-password-input"]';
  private readonly signupButton = '[data-testid="signup-submit"]';
  private readonly errorMessage = '[data-testid="error-message"]';
  private readonly successMessage = '[data-testid="success-message"]';
  private readonly termsCheckbox = '[data-testid="terms-checkbox"]';
  private readonly loginLink = '[data-testid="login-link"]';

  constructor(page: Page) {
    super(page, '/signup');
  }

  async navigateToSignup(): Promise<void> {
    await this.navigate();
  }

  async enterFullName(fullName: string): Promise<void> {
    await this.fillInput(this.fullNameInput, fullName);
  }

  async enterEmail(email: string): Promise<void> {
    await this.fillInput(this.emailInput, email);
  }

  async enterPhone(phone: string): Promise<void> {
    await this.fillInput(this.phoneInput, phone);
  }

  async enterPassword(password: string): Promise<void> {
    await this.fillInput(this.passwordInput, password);
  }

  async enterConfirmPassword(password: string): Promise<void> {
    await this.fillInput(this.confirmPasswordInput, password);
  }

  async clickSignupButton(): Promise<void> {
    await this.clickElement(this.signupButton);
    await this.waitForNavigation();
  }

  async signup(userData: {
    fullName: string;
    email: string;
    phone: string;
    password: string;
    confirmPassword: string;
  }): Promise<void> {
    await this.enterFullName(userData.fullName);
    await this.enterEmail(userData.email);
    await this.enterPhone(userData.phone);
    await this.enterPassword(userData.password);
    await this.enterConfirmPassword(userData.confirmPassword);
    await this.clickSignupButton();
  }

  async checkTermsAndConditions(): Promise<void> {
    await this.checkCheckbox(this.termsCheckbox);
  }

  async getErrorMessage(): Promise<string> {
    return await this.getText(this.errorMessage);
  }

  async getSuccessMessage(): Promise<string> {
    return await this.getText(this.successMessage);
  }

  async isErrorMessageVisible(): Promise<boolean> {
    return await this.isVisible(this.errorMessage);
  }

  async isSuccessMessageVisible(): Promise<boolean> {
    return await this.isVisible(this.successMessage);
  }

  async clickLoginLink(): Promise<void> {
    await this.clickElement(this.loginLink);
  }

  async isSignupButtonEnabled(): Promise<boolean> {
    return await this.isElementEnabled(this.signupButton);
  }

  async waitForSignupSuccess(): Promise<void> {
    await this.page.waitForURL(/login|dashboard/, { timeout: 10000 });
  }

  async validateEmailField(): Promise<boolean> {
    const emailInput = this.page.locator(this.emailInput);
    const email = await emailInput.inputValue();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  async validatePhoneField(): Promise<boolean> {
    const phoneInput = this.page.locator(this.phoneInput);
    const phone = await phoneInput.inputValue();
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
  }
}
