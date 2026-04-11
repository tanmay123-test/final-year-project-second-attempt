import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class FinnyPage extends BasePage {
  // Selectors
  private readonly chatInput = '[data-testid="chat-input"]';
  private readonly sendButton = '[data-testid="send-button"]';
  private readonly chatMessages = '[data-testid="chat-messages"]';
  private readonly dashboardButton = '[data-testid="dashboard-btn"]';
  private readonly chatModeButton = '[data-testid="chat-mode-btn"]';
  private readonly portfolioButton = '[data-testid="portfolio-btn"]';
  private readonly addTransactionButton = '[data-testid="add-transaction-btn"]';
  private readonly transactionForm = '[data-testid="transaction-form"]';
  private readonly todaySummary = '[data-testid="today-summary"]';
  private readonly monthlyChart = '[data-testid="monthly-chart"]';

  constructor(page: Page) {
    super(page, '/finny');
  }

  async navigateToFinny(): Promise<void> {
    await this.navigate();
  }

  async isFinnyPageLoaded(): Promise<boolean> {
    return await this.isVisible(this.chatInput) || 
           await this.isVisible(this.dashboardButton);
  }

  async enterChatMessage(message: string): Promise<void> {
    await this.fillInput(this.chatInput, message);
  }

  async clickSendButton(): Promise<void> {
    await this.clickElement(this.sendButton);
  }

  async sendMessage(message: string): Promise<void> {
    await this.enterChatMessage(message);
    await this.clickSendButton();
    await this.page.waitForTimeout(2000); // Wait for response
  }

  async getLastMessage(): Promise<string> {
    const messages = await this.page.locator(this.chatMessages).all();
    const lastMessage = messages[messages.length - 1];
    return await lastMessage.textContent() || '';
  }

  async getChatMessageCount(): Promise<number> {
    return await this.page.locator(this.chatMessages).count();
  }

  async clickDashboard(): Promise<void> {
    await this.clickElement(this.dashboardButton);
    await this.waitForNavigation();
  }

  async clickChatMode(): Promise<void> {
    await this.clickElement(this.chatModeButton);
    await this.waitForNavigation();
  }

  async clickPortfolio(): Promise<void> {
    await this.clickElement(this.portfolioButton);
    await this.waitForNavigation();
  }

  async clickAddTransaction(): Promise<void> {
    await this.clickElement(this.addTransactionButton);
  }

  async isTransactionFormVisible(): Promise<boolean> {
    return await this.isVisible(this.transactionForm);
  }

  async addTransaction(transactionData: {
    amount: string;
    category: string;
    description: string;
    date: string;
  }): Promise<void> {
    await this.fillInput('[data-testid="transaction-amount"]', transactionData.amount);
    await this.selectOption('[data-testid="transaction-category"]', transactionData.category);
    await this.fillInput('[data-testid="transaction-description"]', transactionData.description);
    await this.fillInput('[data-testid="transaction-date"]', transactionData.date);
    await this.clickElement('[data-testid="save-transaction"]');
    await this.page.waitForTimeout(2000);
  }

  async getTodayTotal(): Promise<string> {
    return await this.getText('[data-testid="today-total"]');
  }

  async getTodayTransactionCount(): Promise<number> {
    const countText = await this.getText('[data-testid="transaction-count"]');
    const match = countText.match(/\d+/);
    return match ? parseInt(match[0]) : 0;
  }

  async getCategoryBreakdown(): Promise<Map<string, number>> {
    const categories = new Map<string, number>();
    const categoryElements = await this.page.locator('[data-testid="category-item"]').all();
    
    for (const element of categoryElements) {
      const name = await element.locator('[data-testid="category-name"]').textContent() || '';
      const amountText = await element.locator('[data-testid="category-amount"]').textContent() || '';
      const amount = parseFloat(amountText.replace(/[^0-9.]/g, ''));
      categories.set(name, amount);
    }
    
    return categories;
  }

  async isChartVisible(): Promise<boolean> {
    return await this.isVisible(this.monthlyChart);
  }

  async waitForAiResponse(): Promise<void> {
    await this.page.waitForSelector('[data-testid="ai-message"]', { timeout: 10000 });
  }

  async getAiResponse(): Promise<string> {
    await this.waitForAiResponse();
    return await this.getText('[data-testid="ai-message"]');
  }

  async clearChat(): Promise<void> {
    await this.clickElement('[data-testid="clear-chat"]');
    await this.page.waitForTimeout(1000);
  }

  async isTypingIndicatorVisible(): Promise<boolean> {
    return await this.isVisible('[data-testid="typing-indicator"]');
  }

  async exportData(): Promise<void> {
    await this.clickElement('[data-testid="export-data"]');
    await this.page.waitForTimeout(2000);
  }

  async searchTransactions(searchTerm: string): Promise<void> {
    await this.fillInput('[data-testid="search-transactions"]', searchTerm);
    await this.page.waitForTimeout(2000);
  }

  async filterByDateRange(startDate: string, endDate: string): Promise<void> {
    await this.fillInput('[data-testid="start-date"]', startDate);
    await this.fillInput('[data-testid="end-date"]', endDate);
    await this.clickElement('[data-testid="apply-filter"]');
    await this.page.waitForTimeout(2000);
  }
}
