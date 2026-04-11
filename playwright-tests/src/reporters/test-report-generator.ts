import { TestCaseResult, TestSummary } from '../types';
import * as fs from 'fs';
import * as path from 'path';

export class TestReportGenerator {
  private testResults: TestCaseResult[] = [];
  private testSummary: TestSummary | null = null;

  addTestResult(result: TestCaseResult): void {
    this.testResults.push(result);
  }

  setTestSummary(summary: TestSummary): void {
    this.testSummary = summary;
  }

  generateTestReport(): string {
    const report = this.buildTestReport();
    this.saveReportToFile(report, 'test-report.md');
    return report;
  }

  private buildTestReport(): string {
    let report = '# ExpertEase E2E Test Report\n\n';
    report += `**Generated on:** ${new Date().toLocaleString()}\n\n`;

    if (this.testSummary) {
      report += this.buildTestSummarySection();
    }

    report += this.buildTestResultsTable();
    report += this.buildDetailedTestCases();

    return report;
  }

  private buildTestSummarySection(): string {
    let section = '## Test Summary\n\n';
    section += '| Metric | Value |\n';
    section += '|--------|-------|\n';
    section += `| Total Tests | ${this.testSummary!.totalTests} |\n`;
    section += `| Passed | ${this.testSummary!.passedTests} |\n`;
    section += `| Failed | ${this.testSummary!.failedTests} |\n`;
    section += `| Skipped | ${this.testSummary!.skippedTests} |\n`;
    section += `| Pass Rate | ${this.testSummary!.passRate.toFixed(2)}% |\n`;
    section += `| Total Duration | ${this.formatDuration(this.testSummary!.totalDuration)} |\n\n`;
    
    return section;
  }

  private buildTestResultsTable(): string {
    let table = '## Test Results Overview\n\n';
    table += '| Test Case ID | Objectives | Status | Duration |\n';
    table += '|--------------|------------|--------|----------|\n';

    this.testResults.forEach(result => {
      const status = result.status === 'PASS' ? '✅ PASS' : '❌ FAIL';
      table += `| ${result.testCaseId} | ${result.objective} | ${status} | ${this.formatDuration(result.duration)} |\n`;
    });

    table += '\n';
    return table;
  }

  private buildDetailedTestCases(): string {
    let details = '## Detailed Test Cases\n\n';

    this.testResults.forEach((result, index) => {
      details += `### Test Case ${index + 1}: ${result.testCaseId}\n\n`;
      details += '**Objective:** ' + result.objective + '\n\n';
      
      details += '**Steps:**\n';
      result.steps.forEach((step, stepIndex) => {
        details += `${stepIndex + 1}. ${step}\n`;
      });
      details += '\n';

      details += '**Expected Output:**\n';
      details += '```\n' + result.expectedOutput + '\n```\n\n';

      details += '**Actual Output:**\n';
      details += '```\n' + result.actualOutput + '\n```\n\n';

      details += '**Status:** ' + (result.status === 'PASS' ? '✅ PASS' : '❌ FAIL') + '\n\n';

      if (result.screenshot) {
        details += '**Screenshot:**\n';
        details += `![Screenshot](${result.screenshot})\n\n`;
      }

      if (result.error) {
        details += '**Error:**\n';
        details += '```\n' + result.error + '\n```\n\n';
      }

      details += '---\n\n';
    });

    return details;
  }

  private formatDuration(ms: number): string {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  }

  private saveReportToFile(content: string, filename: string): void {
    const reportPath = path.join(process.cwd(), filename);
    fs.writeFileSync(reportPath, content, 'utf8');
    console.log(`📊 Test report generated: ${reportPath}`);
  }

  clearResults(): void {
    this.testResults = [];
    this.testSummary = null;
  }

  getResults(): TestCaseResult[] {
    return [...this.testResults];
  }

  getFailedTests(): TestCaseResult[] {
    return this.testResults.filter(result => result.status === 'FAIL');
  }
}
