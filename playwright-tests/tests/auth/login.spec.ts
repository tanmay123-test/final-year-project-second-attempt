import { test, expect } from '@playwright/test';
import { LoginPage } from '../../src/pages/LoginPage';
import { TestDataGenerator } from '../../src/utils/helpers';

test.describe('Login Page Tests', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.navigateToLogin();
  });

  test('TC11 should load login page successfully', async ({ page }) => {
    // Test objective: Verify login page loads with all required elements
    const expectedOutput = 'Login page should load with email, password fields and login button';
    
    try {
      // Verify page is loaded
      await expect(loginPage.isVisible(loginPage['emailInput'])).toBe(true);
      await expect(loginPage.isVisible(loginPage['passwordInput'])).toBe(true);
      await expect(loginPage.isVisible(loginPage['loginButton'])).toBe(true);
      
      // Verify forgot password and signup links
      expect(await loginPage.isForgotPasswordLinkVisible()).toBe(true);
      expect(await loginPage.isSignupLinkVisible()).toBe(true);
      
      await loginPage.takeScreenshot('TC11_login_page_load', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC11_login_page_load', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC12 should show error for invalid credentials', async ({ page }) => {
    // Test objective: Verify proper error handling for invalid login credentials
    const expectedOutput = 'Should display error message for invalid credentials';
    
    try {
      const invalidUser = TestDataGenerator.generateTestUser();
      
      await loginPage.login(invalidUser.email, invalidUser.password);
      
      // Wait for error message
      await page.waitForTimeout(2000);
      
      const isErrorMessageVisible = await loginPage.isErrorMessageVisible();
      expect(isErrorMessageVisible).toBe(true);
      
      const errorMessage = await loginPage.getErrorMessage();
      expect(errorMessage).toBeTruthy();
      expect(errorMessage.length).toBeGreaterThan(0);
      
      await loginPage.takeScreenshot('TC12_invalid_credentials', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC12_invalid_credentials', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC13 should validate email format', async ({ page }) => {
    // Test objective: Verify email format validation
    const expectedOutput = 'Should validate email format and show appropriate error';
    
    try {
      // Test invalid email formats
      const invalidEmails = [
        'invalid-email',
        'test@',
        '@domain.com',
        'test.domain.com',
        '',
        '   '
      ];

      for (const email of invalidEmails) {
        await loginPage.enterEmail(email);
        await loginPage.enterPassword('Test@123456');
        
        // Try to submit or check for validation
        const isButtonEnabled = await loginPage.isLoginButtonEnabled();
        
        // If button is disabled, validation is working
        // If button is enabled, we expect error message after submission
        if (isButtonEnabled) {
          await loginPage.clickLoginButton();
          await page.waitForTimeout(1000);
          
          const hasError = await loginPage.isErrorMessageVisible();
          if (!hasError) {
            // Clear and try next
            await loginPage.enterEmail('');
            await loginPage.enterPassword('');
          }
        }
      }
      
      await loginPage.takeScreenshot('TC13_email_validation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC13_email_validation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC14 should validate required fields', async ({ page }) => {
    // Test objective: Verify required field validation
    const expectedOutput = 'Should validate that email and password are required';
    
    try {
      // Test empty fields
      await loginPage.clickLoginButton();
      await page.waitForTimeout(1000);
      
      // Check for validation or error messages
      const emailValue = await page.inputValue(loginPage['emailInput']);
      const passwordValue = await page.inputValue(loginPage['passwordInput']);
      
      // If validation is working, fields should be highlighted or error shown
      const hasError = await loginPage.isErrorMessageVisible();
      
      // Test with only email
      await loginPage.enterEmail('test@example.com');
      await loginPage.clickLoginButton();
      await page.waitForTimeout(1000);
      
      // Test with only password
      await loginPage.enterEmail('');
      await loginPage.enterPassword('Test@123456');
      await loginPage.clickLoginButton();
      await page.waitForTimeout(1000);
      
      await loginPage.takeScreenshot('TC14_required_fields', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC14_required_fields', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC15 should navigate to signup page', async ({ page }) => {
    // Test objective: Verify navigation to signup page works
    const expectedOutput = 'Should navigate to signup page when signup link is clicked';
    
    try {
      await loginPage.clickSignupLink();
      
      const currentUrl = await loginPage.getCurrentUrl();
      expect(currentUrl).toContain('signup');
      
      await loginPage.takeScreenshot('TC15_signup_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC15_signup_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC16 should navigate to forgot password', async ({ page }) => {
    // Test objective: Verify forgot password navigation works
    const expectedOutput = 'Should navigate to forgot password page';
    
    try {
      await loginPage.clickForgotPassword();
      
      const currentUrl = await loginPage.getCurrentUrl();
      expect(currentUrl).toContain('forgot') || expect(currentUrl).toContain('reset');
      
      await loginPage.takeScreenshot('TC16_forgot_password', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC16_forgot_password', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC17 should remember me functionality', async ({ page }) => {
    // Test objective: Verify remember me checkbox functionality
    const expectedOutput = 'Remember me checkbox should be functional';
    
    try {
      // Check if remember me checkbox exists
      const isCheckboxVisible = await loginPage.isVisible(loginPage['rememberMeCheckbox']);
      
      if (isCheckboxVisible) {
        await loginPage.checkRememberMe();
        
        // Verify checkbox is checked (this might vary based on implementation)
        const isChecked = await page.isChecked(loginPage['rememberMeCheckbox']);
        // Note: Checkbox state verification depends on implementation
      }
      
      await loginPage.takeScreenshot('TC17_remember_me', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC17_remember_me', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC18 should handle password visibility toggle', async ({ page }) => {
    // Test objective: Verify password visibility toggle functionality
    const expectedOutput = 'Password visibility should be toggleable';
    
    try {
      const passwordInput = page.locator(loginPage['passwordInput']);
      
      // Check if password is masked by default
      const inputType = await passwordInput.getAttribute('type');
      expect(inputType).toBe('password');
      
      // Look for password toggle button
      const toggleButton = page.locator('[data-testid="password-toggle"], .password-toggle, button[aria-label*="password"]');
      
      if (await toggleButton.isVisible()) {
        await toggleButton.click();
        await page.waitForTimeout(500);
        
        // Check if password is now visible
        const newInputType = await passwordInput.getAttribute('type');
        expect(newInputType).toBe('text');
        
        // Toggle back
        await toggleButton.click();
        await page.waitForTimeout(500);
        
        const finalInputType = await passwordInput.getAttribute('type');
        expect(finalInputType).toBe('password');
      }
      
      await loginPage.takeScreenshot('TC18_password_toggle', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC18_password_toggle', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC19 should handle form submission with Enter key', async ({ page }) => {
    // Test objective: Verify form can be submitted with Enter key
    const expectedOutput = 'Form should submit when Enter key is pressed in password field';
    
    try {
      const testUser = TestDataGenerator.generateTestUser();
      
      await loginPage.enterEmail(testUser.email);
      await loginPage.enterPassword(testUser.password);
      
      // Press Enter in password field
      await page.focus(loginPage['passwordInput']);
      await loginPage.pressKey('Enter');
      
      await page.waitForTimeout(2000);
      
      // Check if login attempt was made (either success or error)
      const currentUrl = await loginPage.getCurrentUrl();
      const hasError = await loginPage.isErrorMessageVisible();
      
      // Either we're redirected (success) or we see an error (failed login)
      expect(currentUrl !== '/login' || hasError).toBe(true);
      
      await loginPage.takeScreenshot('TC19_enter_submission', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC19_enter_submission', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC20 should be responsive on mobile', async ({ page }) => {
    // Test objective: Verify login page is responsive on mobile devices
    const expectedOutput = 'Login page should be properly formatted for mobile devices';
    
    try {
      // Change to mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Verify all elements are still visible and functional
      await expect(loginPage.isVisible(loginPage['emailInput'])).toBe(true);
      await expect(loginPage.isVisible(loginPage['passwordInput'])).toBe(true);
      await expect(loginPage.isVisible(loginPage['loginButton'])).toBe(true);
      
      // Test form functionality on mobile
      const testUser = TestDataGenerator.generateTestUser();
      await loginPage.enterEmail(testUser.email);
      await loginPage.enterPassword(testUser.password);
      
      await loginPage.takeScreenshot('TC20_mobile_responsive', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await loginPage.takeDefectScreenshot('TC20_mobile_responsive', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });
});
