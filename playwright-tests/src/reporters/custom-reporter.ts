import { Reporter, TestCase, TestResult, FullResult } from '@playwright/test/reporter';
import { TestReportGenerator } from './test-report-generator';
import { DefectReportGenerator } from './defect-report-generator';
import { TestCaseResult, TestSummary, DefectReport } from '../types';
import { TestUtils } from '../utils/helpers';

class CustomReporter implements Reporter {
  private testReportGenerator = new TestReportGenerator();
  private defectReportGenerator = new DefectReportGenerator();
  private testResults: TestCaseResult[] = [];
  private startTime: number = Date.now();

  onTestBegin(test: TestCase): void {
    console.log(`🧪 Starting test: ${test.title}`);
  }

  onTestEnd(test: TestCase, result: TestResult): void {
    console.log(`📝 Test completed: ${test.title} - ${result.status}`);
    
    const testCaseResult = this.createTestCaseResult(test, result);
    this.testResults.push(testCaseResult);
    this.testReportGenerator.addTestResult(testCaseResult);

    if (result.status === 'failed') {
      const defect = this.createDefectFromTestResult(test, result, testCaseResult);
      this.defectReportGenerator.addDefect(defect);
    }
  }

  onEnd(result: FullResult): void {
    console.log('🏁 Test suite completed. Generating reports...');
    
    const endTime = Date.now();
    const totalDuration = endTime - this.startTime;
    
    const testSummary = this.createTestSummary(result, totalDuration);
    this.testReportGenerator.setTestSummary(testSummary);

    // Generate reports
    this.testReportGenerator.generateTestReport();
    this.defectReportGenerator.generateDefectReport();

    // Print summary to console
    this.printConsoleSummary(testSummary);
  }

  private createTestCaseResult(test: TestCase, result: TestResult): TestCaseResult {
    const steps = this.extractStepsFromTest(test);
    const duration = result.duration;
    const status = result.status === 'passed' ? 'PASS' : 'FAIL';
    
    return {
      testCaseId: this.generateTestCaseId(test.title),
      objective: this.extractObjectiveFromTest(test),
      steps: steps,
      expectedOutput: this.extractExpectedOutput(test),
      actualOutput: this.extractActualOutput(result),
      status: status,
      screenshot: this.getScreenshotPath(result),
      timestamp: new Date(),
      duration: duration,
      error: result.error?.message
    };
  }

  private createDefectFromTestResult(
    test: TestCase, 
    result: TestResult, 
    testCaseResult: TestCaseResult
  ): DefectReport {
    return this.defectReportGenerator.createDefectFromTestResult(
      testCaseResult.testCaseId,
      this.extractModuleFromTest(test),
      `Test Failed: ${test.title}`,
      `The test case "${test.title}" failed during execution.`,
      testCaseResult.steps,
      testCaseResult.actualOutput,
      testCaseResult.expectedOutput,
      testCaseResult.screenshot,
      result.error?.message
    );
  }

  private createTestSummary(result: FullResult, totalDuration: number): TestSummary {
    const allResults = result.results || [];
    const passedTests = allResults.filter(r => r.status === 'passed').length;
    const failedTests = allResults.filter(r => r.status === 'failed').length;
    const skippedTests = allResults.filter(r => r.status === 'skipped').length;
    const totalTests = allResults.length;

    return {
      totalTests,
      passedTests,
      failedTests,
      skippedTests,
      totalDuration,
      passRate: totalTests > 0 ? (passedTests / totalTests) * 100 : 0,
      timestamp: new Date()
    };
  }

  private generateTestCaseId(testTitle: string): string {
    const module = this.extractModuleFromTestTitle(testTitle);
    const index = this.testResults.filter(t => 
      this.extractModuleFromTestTitle(t.testCaseId) === module
    ).length + 1;
    
    return TestUtils.generateTestCaseId(module, index);
  }

  private extractModuleFromTest(test: TestCase): string {
    return this.extractModuleFromTestTitle(test.title);
  }

  private extractModuleFromTestTitle(testTitle: string): string {
    const titleLower = testTitle.toLowerCase();
    
    if (titleLower.includes('home')) return 'Home';
    if (titleLower.includes('login')) return 'Login';
    if (titleLower.includes('signup')) return 'Signup';
    if (titleLower.includes('healthcare')) return 'Healthcare';
    if (titleLower.includes('finny') || titleLower.includes('money')) return 'Finny';
    if (titleLower.includes('freelance')) return 'Freelance';
    if (titleLower.includes('car')) return 'Car';
    if (titleLower.includes('housekeeping')) return 'Housekeeping';
    
    return 'General';
  }

  private extractObjectiveFromTest(test: TestCase): string {
    // Extract objective from test title or annotations
    const title = test.title;
    
    if (title.includes('should')) {
      return title.replace(/.*should\s+/i, '');
    }
    
    return title;
  }

  private extractStepsFromTest(test: TestCase): string[] {
    // This would ideally be extracted from test annotations or comments
    // For now, we'll create generic steps
    return [
      `Navigate to test page: ${test.title}`,
      'Execute test actions',
      'Verify expected results'
    ];
  }

  private extractExpectedOutput(test: TestCase): string {
    // Extract expected output from test title or annotations
    const title = test.title.toLowerCase();
    
    if (title.includes('should display')) {
      return 'Expected content should be displayed correctly';
    }
    if (title.includes('should navigate')) {
      return 'User should be navigated to the correct page';
    }
    if (title.includes('should login')) {
      return 'User should be successfully logged in';
    }
    if (title.includes('should signup')) {
      return 'User should be successfully registered';
    }
    
    return 'Test should execute successfully without errors';
  }

  private extractActualOutput(result: TestResult): string {
    if (result.status === 'passed') {
      return 'Test executed successfully - all assertions passed';
    }
    
    if (result.error) {
      return `Test failed with error: ${result.error.message}`;
    }
    
    return 'Test execution completed';
  }

  private getScreenshotPath(result: TestResult): string {
    // Extract screenshot path from test result attachments
    const screenshotAttachment = result.attachments?.find(
      attachment => attachment.name === 'screenshot' || attachment.contentType?.startsWith('image/')
    );
    
    if (screenshotAttachment && screenshotAttachment.path) {
      return screenshotAttachment.path;
    }
    
    // Fallback to default path
    return './test-results/screenshots/default.png';
  }

  private printConsoleSummary(summary: TestSummary): void {
    console.log('\n📊 ===== TEST EXECUTION SUMMARY =====');
    console.log(`Total Tests: ${summary.totalTests}`);
    console.log(`✅ Passed: ${summary.passedTests}`);
    console.log(`❌ Failed: ${summary.failedTests}`);
    console.log(`⏭️  Skipped: ${summary.skippedTests}`);
    console.log(`📈 Pass Rate: ${summary.passRate.toFixed(2)}%`);
    console.log(`⏱️  Duration: ${TestUtils.formatDuration(summary.totalDuration)}`);
    console.log('=====================================\n');

    if (summary.failedTests > 0) {
      console.log(`🐛 ${summary.failedTests} defect(s) found. Check defect-report.md for details.`);
    } else {
      console.log('🎉 All tests passed! No defects detected.');
    }

    console.log('📄 Reports generated:');
    console.log('   - test-report.md');
    console.log('   - defect-report.md');
  }
}

export default CustomReporter;
