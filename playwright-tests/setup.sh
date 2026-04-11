#!/bin/bash

echo "🔧 Setting up Playwright E2E Test Suite..."
echo "=========================================="

# Navigate to test directory
cd playwright-tests

echo "📦 Installing dependencies..."
npm install

echo "🌐 Installing Playwright browsers..."
npx playwright install

echo "🔍 Verifying installation..."
npx playwright --version

echo "✅ Setup complete!"
echo ""
echo "🚀 Run tests with:"
echo "   npm test                    # Run all tests"
echo "   npm run test:headed         # Visible browser"
echo "   npm run test:report         # With custom reporting"
echo ""
echo "📊 Reports will be generated in:"
echo "   - test-report.md"
echo "   - defect-report.md"
echo "   - playwright-report/index.html"
