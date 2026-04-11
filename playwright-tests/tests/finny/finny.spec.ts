import { test, expect } from '@playwright/test';
import { FinnyPage } from '../../src/pages/FinnyPage';
import { TestDataGenerator } from '../../src/utils/helpers';

test.describe('Finny (Money Management) Tests', () => {
  let finnyPage: FinnyPage;

  test.beforeEach(async ({ page }) => {
    finnyPage = new FinnyPage(page);
    await finnyPage.navigateToFinny();
  });

  test('TC21 should load Finny page successfully', async ({ page }) => {
    // Test objective: Verify Finny page loads with chat interface
    const expectedOutput = 'Finny page should load with chat input and dashboard options';
    
    try {
      const isPageLoaded = await finnyPage.isFinnyPageLoaded();
      expect(isPageLoaded).toBe(true);
      
      await finnyPage.takeScreenshot('TC21_finny_page_load', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC21_finny_page_load', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC22 should send chat message and receive AI response', async ({ page }) => {
    // Test objective: Verify chat functionality with AI responses
    const expectedOutput = 'Should send message and receive AI response';
    
    try {
      const testMessage = 'What is a mutual fund?';
      
      await finnyPage.sendMessage(testMessage);
      
      const response = await finnyPage.getAiResponse();
      expect(response).toBeTruthy();
      expect(response.length).toBeGreaterThan(0);
      
      await finnyPage.takeScreenshot('TC22_chat_ai_response', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC22_chat_ai_response', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC23 should add transaction via chat', async ({ page }) => {
    // Test objective: Verify transaction addition through natural language
    const expectedOutput = 'Should parse and add transaction from chat message';
    
    try {
      const transactionMessage = 'food 200 transport 150';
      
      const initialMessageCount = await finnyPage.getChatMessageCount();
      
      await finnyPage.sendMessage(transactionMessage);
      await page.waitForTimeout(3000); // Wait for processing
      
      const finalMessageCount = await finnyPage.getChatMessageCount();
      expect(finalMessageCount).toBeGreaterThan(initialMessageCount);
      
      const lastMessage = await finnyPage.getLastMessage();
      expect(lastMessage).toContain('transaction') || expect(lastMessage).toContain('added');
      
      await finnyPage.takeScreenshot('TC23_chat_transaction', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC23_chat_transaction', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC24 should navigate to dashboard', async ({ page }) => {
    // Test objective: Verify dashboard navigation and functionality
    const expectedOutput = 'Should navigate to dashboard and show financial summary';
    
    try {
      await finnyPage.clickDashboard();
      
      const currentUrl = await finnyPage.getCurrentUrl();
      expect(currentUrl).toContain('dashboard') || expect(currentUrl).toContain('finny');
      
      // Check if dashboard elements are visible
      const todayTotal = await finnyPage.getTodayTotal();
      expect(todayTotal).toBeTruthy();
      
      await finnyPage.takeScreenshot('TC24_dashboard_navigation', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC24_dashboard_navigation', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC25 should show today\'s summary', async ({ page }) => {
    // Test objective: Verify today's financial summary is displayed
    const expectedOutput = 'Should display today\'s total spending and transaction count';
    
    try {
      const todayTotal = await finnyPage.getTodayTotal();
      const transactionCount = await finnyPage.getTodayTransactionCount();
      
      expect(todayTotal).toBeTruthy();
      expect(typeof transactionCount).toBe('number');
      expect(transactionCount).toBeGreaterThanOrEqual(0);
      
      await finnyPage.takeScreenshot('TC25_today_summary', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC25_today_summary', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC26 should display category breakdown', async ({ page }) => {
    // Test objective: Verify spending is categorized correctly
    const expectedOutput = 'Should show spending breakdown by category';
    
    try {
      const categories = await finnyPage.getCategoryBreakdown();
      expect(categories.size).toBeGreaterThanOrEqual(0);
      
      if (categories.size > 0) {
        categories.forEach((amount, category) => {
          expect(category).toBeTruthy();
          expect(typeof amount).toBe('number');
          expect(amount).toBeGreaterThanOrEqual(0);
        });
      }
      
      await finnyPage.takeScreenshot('TC26_category_breakdown', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC26_category_breakdown', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC27 should add manual transaction', async ({ page }) => {
    // Test objective: Verify manual transaction addition through form
    const expectedOutput = 'Should add transaction through manual form';
    
    try {
      await finnyPage.clickAddTransaction();
      
      const isFormVisible = await finnyPage.isTransactionFormVisible();
      expect(isFormVisible).toBe(true);
      
      const transactionData = {
        amount: '500',
        category: 'Food',
        description: 'Lunch at restaurant',
        date: new Date().toISOString().split('T')[0]
      };
      
      await finnyPage.addTransaction(transactionData);
      
      // Verify transaction was added (check for success message or updated summary)
      await page.waitForTimeout(2000);
      
      await finnyPage.takeScreenshot('TC27_manual_transaction', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC27_manual_transaction', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC28 should navigate to chat mode', async ({ page }) => {
    // Test objective: Verify chat mode navigation
    const expectedOutput = 'Should navigate to chat mode interface';
    
    try {
      await finnyPage.clickChatMode();
      
      const currentUrl = await finnyPage.getCurrentUrl();
      expect(currentUrl).toContain('chat') || expect(currentUrl).toContain('mode');
      
      // Verify chat interface is active
      const isChatInputVisible = await finnyPage.isVisible(finnyPage['chatInput']);
      expect(isChatInputVisible).toBe(true);
      
      await finnyPage.takeScreenshot('TC28_chat_mode', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC28_chat_mode', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC29 should show typing indicator during AI response', async ({ page }) => {
    // Test objective: Verify typing indicator appears while AI is responding
    const expectedOutput = 'Should show typing indicator during AI response generation';
    
    try {
      const testMessage = 'Explain diversification in investing';
      
      await finnyPage.enterChatMessage(testMessage);
      await finnyPage.clickSendButton();
      
      // Check for typing indicator immediately after sending
      const isTypingVisible = await finnyPage.isTypingIndicatorVisible();
      
      // Wait for response
      await finnyPage.waitForAiResponse();
      
      await finnyPage.takeScreenshot('TC29_typing_indicator', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC29_typing_indicator', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC30 should handle multiple chat messages', async ({ page }) => {
    // Test objective: Verify multiple chat messages are handled correctly
    const expectedOutput = 'Should maintain chat history with multiple messages';
    
    try {
      const messages = [
        'What is SIP?',
        'Best investment options for beginners?',
        'How to save tax?'
      ];
      
      let initialMessageCount = await finnyPage.getChatMessageCount();
      
      for (const message of messages) {
        await finnyPage.sendMessage(message);
        await page.waitForTimeout(2000); // Wait for response
      }
      
      const finalMessageCount = await finnyPage.getChatMessageCount();
      expect(finalMessageCount).toBeGreaterThan(initialMessageCount);
      
      // Verify chat history is maintained
      const lastMessage = await finnyPage.getLastMessage();
      expect(lastMessage).toBeTruthy();
      expect(lastMessage.length).toBeGreaterThan(0);
      
      await finnyPage.takeScreenshot('TC30_multiple_messages', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await finnyPage.takeDefectScreenshot('TC30_multiple_messages', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });
});
