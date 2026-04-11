import { DefectReport } from '../types';
import * as fs from 'fs';
import * as path from 'path';

export class DefectReportGenerator {
  private defects: DefectReport[] = [];

  addDefect(defect: DefectReport): void {
    this.defects.push(defect);
  }

  generateDefectReport(): string {
    const report = this.buildDefectReport();
    this.saveReportToFile(report, 'defect-report.md');
    return report;
  }

  private buildDefectReport(): string {
    let report = '# ExpertEase Defect Report (MSBTE K Scheme)\n\n';
    report += `**Generated on:** ${new Date().toLocaleString()}\n`;
    report += `**Total Defects:** ${this.defects.length}\n\n`;

    if (this.defects.length === 0) {
      report += '🎉 **No defects found! All tests passed successfully.**\n';
      return report;
    }

    // Add defect summary
    report += this.buildDefectSummary();

    // Add detailed defect reports
    this.defects.forEach((defect, index) => {
      report += this.buildIndividualDefectReport(defect, index + 1);
    });

    return report;
  }

  private buildDefectSummary(): string {
    let summary = '## Defect Summary\n\n';
    
    const severityCount = {
      High: this.defects.filter(d => d.severity === 'High').length,
      Medium: this.defects.filter(d => d.severity === 'Medium').length,
      Low: this.defects.filter(d => d.severity === 'Low').length
    };

    summary += '| Severity | Count |\n';
    summary += '|----------|-------|\n';
    summary += `| High | ${severityCount.High} |\n`;
    summary += `| Medium | ${severityCount.Medium} |\n`;
    summary += `| Low | ${severityCount.Low} |\n\n`;

    const priorityCount = {
      High: this.defects.filter(d => d.priority === 'High').length,
      Medium: this.defects.filter(d => d.priority === 'Medium').length,
      Low: this.defects.filter(d => d.priority === 'Low').length
    };

    summary += '| Priority | Count |\n';
    summary += '|----------|-------|\n';
    summary += `| High | ${priorityCount.High} |\n`;
    summary += `| Medium | ${priorityCount.Medium} |\n`;
    summary += `| Low | ${priorityCount.Low} |\n\n`;

    return summary;
  }

  private buildIndividualDefectReport(defect: DefectReport, index: number): string {
    let report = `## Defect #${index}: ${defect.summary}\n\n`;

    // MSBTE K Scheme Format Table
    report += '| Field | Value |\n';
    report += '|-------|-------|\n';
    report += `| ID | ${defect.id} |\n`;
    report += `| Project | ${defect.project} |\n`;
    report += `| Product | ${defect.product} |\n`;
    report += `| Release Version | ${defect.releaseVersion} |\n`;
    report += `| Module | ${defect.module} |\n`;
    report += `| Detected Build Version | ${defect.detectedBuildVersion} |\n`;
    report += `| Summary | ${defect.summary} |\n`;
    report += `| Defect Severity & Priority | ${defect.severity} / ${defect.priority} |\n`;
    report += `| Reported By | ${defect.reportedBy} |\n`;
    report += `| Status | ${defect.status} |\n\n`;

    // Detailed Description
    report += '**Description:**\n';
    report += defect.description + '\n\n';

    // Steps to Replicate
    report += '**Steps to Replicate:**\n';
    defect.stepsToReplicate.forEach((step, stepIndex) => {
      report += `${stepIndex + 1}. ${step}\n`;
    });
    report += '\n';

    // Actual vs Expected Result
    report += '**Actual Result vs Expected Result:**\n\n';
    report += '**Expected Result:**\n';
    report += '```\n' + defect.expectedResult + '\n```\n\n';
    report += '**Actual Result:**\n';
    report += '```\n' + defect.actualResult + '\n```\n\n';

    // Visual Evidence
    if (defect.visualEvidence) {
      report += '**Visual Evidence:**\n';
      report += `![Defect Screenshot](${defect.visualEvidence})\n\n`;
    }

    report += '---\n\n';
    return report;
  }

  private saveReportToFile(content: string, filename: string): void {
    const reportPath = path.join(process.cwd(), filename);
    fs.writeFileSync(reportPath, content, 'utf8');
    console.log(`🐛 Defect report generated: ${reportPath}`);
  }

  clearDefects(): void {
    this.defects = [];
  }

  getDefects(): DefectReport[] {
    return [...this.defects];
  }

  getDefectsBySeverity(severity: 'High' | 'Medium' | 'Low'): DefectReport[] {
    return this.defects.filter(defect => defect.severity === severity);
  }

  getDefectsByPriority(priority: 'High' | 'Medium' | 'Low'): DefectReport[] {
    return this.defects.filter(defect => defect.priority === priority);
  }

  createDefectFromTestResult(
    testCaseId: string,
    module: string,
    summary: string,
    description: string,
    steps: string[],
    actualResult: string,
    expectedResult: string,
    screenshot: string,
    error?: string
  ): DefectReport {
    return {
      id: `DEF-${testCaseId}-${Date.now()}`,
      project: 'ExpertEase',
      product: 'ExpertEase Platform',
      releaseVersion: '1.0.0',
      module: module,
      detectedBuildVersion: 'build-' + new Date().toISOString().slice(0, 10),
      summary: summary,
      description: description + (error ? `\n\n**Error Details:** ${error}` : ''),
      stepsToReplicate: steps,
      actualResult: actualResult,
      expectedResult: expectedResult,
        severity: this.determineSeverity(error, module),
      priority: this.determinePriority(error, module),
      reportedBy: 'Test Engineer (Karunesh)',
      status: 'Assigned',
      visualEvidence: screenshot,
      timestamp: new Date()
    };
  }

  private determineSeverity(error?: string, module?: string): 'High' | 'Medium' | 'Low' {
    if (!error) return 'Medium';
    
    const errorLower = error.toLowerCase();
    
    // High severity errors
    if (errorLower.includes('timeout') || 
        errorLower.includes('crash') || 
        errorLower.includes('server error') ||
        errorLower.includes('500') ||
        errorLower.includes('authentication') ||
        errorLower.includes('authorization')) {
      return 'High';
    }
    
    // Low severity errors
    if (errorLower.includes('not found') || 
        errorLower.includes('404') ||
        errorLower.includes('validation') ||
        errorLower.includes('invalid input')) {
      return 'Low';
    }
    
    return 'Medium';
  }

  private determinePriority(error?: string, module?: string): 'High' | 'Medium' | 'Low' {
    // Critical modules get higher priority
    const criticalModules = ['authentication', 'payment', 'booking', 'login', 'signup'];
    
    if (module && criticalModules.some(critical => module.toLowerCase().includes(critical))) {
      return 'High';
    }
    
    return this.determineSeverity(error, module) as 'High' | 'Medium' | 'Low';
  }
}
