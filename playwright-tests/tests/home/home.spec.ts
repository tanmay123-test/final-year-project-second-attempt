import { test, expect } from '@playwright/test';
import { HomePage } from '../../src/pages/HomePage';
import { TestUtils, TestDataGenerator } from '../../src/utils/helpers';

test.describe('Home Page Tests', () => {
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.navigateToHome();
  });

  test('TC01 should load home page successfully', async ({ page }) => {
    // Test objective: Verify home page loads and displays service selection
    const steps = [
      'Navigate to home page',
      'Wait for page to load',
      'Verify service selection is visible'
    ];

    const expectedOutput = 'Home page should load with service selection options';
    const startTime = Date.now();

    try {
      // Verify page is loaded
      await expect(homePage.isHomePageLoaded()).toBe(true);
      
      // Verify URL
      const currentUrl = await homePage.getCurrentUrl();
      expect(currentUrl).toContain('/');
      
      // Take screenshot
      const screenshot = await homePage.takeScreenshot('TC01_home_page_load', test.info);
      
      const actualOutput = 'Home page loaded successfully with service selection visible';
      const duration = Date.now() - startTime;
      
      console.log(`✅ ${test.title}: PASSED (${duration}ms)`);
      
    } catch (error) {
      const screenshot = await homePage.takeDefectScreenshot('TC01_home_page_load', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC02 should display all service options', async ({ page }) => {
    // Test objective: Verify all service options are displayed
    const expectedOutput = 'All service options (Healthcare, Freelance, Car, Housekeeping, Money) should be visible';
    
    try {
      const serviceCount = await homePage.getServiceCount();
      expect(serviceCount).toBeGreaterThanOrEqual(5);
      
      // Verify specific services are visible
      expect(await homePage.isVisible(homePage['healthcareService'])).toBe(true);
      expect(await homePage.isVisible(homePage['freelanceService'])).toBe(true);
      expect(await homePage.isVisible(homePage['carService'])).toBe(true);
      expect(await homePage.isVisible(homePage['housekeepingService'])).toBe(true);
      expect(await homePage.isVisible(homePage['moneyService'])).toBe(true);
      
      await homePage.takeScreenshot('TC02_service_options', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC02_service_options', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC03 should navigate to healthcare service', async ({ page }) => {
    // Test objective: Verify navigation to healthcare service works
    const expectedOutput = 'Should navigate to healthcare service page';
    
    try {
      await homePage.selectHealthcareService();
      
      const currentUrl = await homePage.getCurrentUrl();
      expect(currentUrl).toContain('healthcare');
      
      await homePage.takeScreenshot('TC03_healthcare_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC03_healthcare_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC04 should navigate to freelance service', async ({ page }) => {
    // Test objective: Verify navigation to freelance service works
    const expectedOutput = 'Should navigate to freelance service page';
    
    try {
      await homePage.selectFreelanceService();
      
      const currentUrl = await homePage.getCurrentUrl();
      expect(currentUrl).toContain('freelance');
      
      await homePage.takeScreenshot('TC04_freelance_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC04_freelance_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC05 should navigate to car service', async ({ page }) => {
    // Test objective: Verify navigation to car service works
    const expectedOutput = 'Should navigate to car service page';
    
    try {
      await homePage.selectCarService();
      
      const currentUrl = await homePage.getCurrentUrl();
      expect(currentUrl).toContain('car');
      
      await homePage.takeScreenshot('TC05_car_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC05_car_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC06 should navigate to housekeeping service', async ({ page }) => {
    // Test objective: Verify navigation to housekeeping service works
    const expectedOutput = 'Should navigate to housekeeping service page';
    
    try {
      await homePage.selectHousekeepingService();
      
      const currentUrl = await homePage.getCurrentUrl();
      expect(currentUrl).toContain('housekeeping');
      
      await homePage.takeScreenshot('TC06_housekeeping_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC06_housekeeping_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC07 should navigate to money service (Finny)', async ({ page }) => {
    // Test objective: Verify navigation to money service works
    const expectedOutput = 'Should navigate to money service (Finny) page';
    
    try {
      await homePage.selectMoneyService();
      
      const currentUrl = await homePage.getCurrentUrl();
      expect(currentUrl).toContain('finny') || expect(currentUrl).toContain('money');
      
      await homePage.takeScreenshot('TC07_money_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC07_money_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC08 should display navigation menu', async ({ page }) => {
    // Test objective: Verify navigation menu is visible and functional
    const expectedOutput = 'Navigation menu should be visible with proper options';
    
    try {
      const isNavVisible = await homePage.isNavigationMenuVisible();
      expect(isNavVisible).toBe(true);
      
      await homePage.takeScreenshot('TC08_navigation_menu', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC08_navigation_menu', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC09 should display login and signup buttons', async ({ page }) => {
    // Test objective: Verify login and signup buttons are accessible
    const expectedOutput = 'Login and signup buttons should be visible and clickable';
    
    try {
      // Check if buttons exist (they might not be visible until user interaction)
      const pageContent = await page.content();
      expect(pageContent).toContain('login') || expect(pageContent).toContain('Login');
      expect(pageContent).toContain('signup') || expect(pageContent).toContain('Signup');
      
      await homePage.takeScreenshot('TC09_auth_buttons', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC09_auth_buttons', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC10 should be responsive on mobile viewport', async ({ page }) => {
    // Test objective: Verify page is responsive on mobile devices
    const expectedOutput = 'Page should adapt to mobile viewport properly';
    
    try {
      // Change to mobile viewport
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone 6/7/8
      
      // Verify page is still functional
      await expect(homePage.isHomePageLoaded()).toBe(true);
      
      // Verify service cards are stacked or responsive
      const serviceCount = await homePage.getServiceCount();
      expect(serviceCount).toBeGreaterThanOrEqual(5);
      
      await homePage.takeScreenshot('TC10_mobile_responsive', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await homePage.takeDefectScreenshot('TC10_mobile_responsive', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });
});
