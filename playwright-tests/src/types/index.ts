export interface TestCaseResult {
  testCaseId: string;
  objective: string;
  steps: string[];
  expectedOutput: string;
  actualOutput: string;
  status: 'PASS' | 'FAIL';
  screenshot: string;
  timestamp: Date;
  duration: number;
  error?: string;
}

export interface DefectReport {
  id: string;
  project: string;
  product: string;
  releaseVersion: string;
  module: string;
  detectedBuildVersion: string;
  summary: string;
  description: string;
  stepsToReplicate: string[];
  actualResult: string;
  expectedResult: string;
  severity: 'High' | 'Medium' | 'Low';
  priority: 'High' | 'Medium' | 'Low';
  reportedBy: string;
  status: string;
  visualEvidence: string;
  timestamp: Date;
}

export interface TestSummary {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  totalDuration: number;
  passRate: number;
  timestamp: Date;
}

export interface PageElements {
  [key: string]: {
    selector: string;
    description: string;
  };
}

export interface TestUserData {
  username?: string;
  email?: string;
  password?: string;
  fullName?: string;
  phone?: string;
}
