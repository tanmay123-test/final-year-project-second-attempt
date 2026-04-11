# ExpertEase E2E Test Suite

## Quick Start

1. **Install Dependencies**
   ```bash
   cd playwright-tests
   npm install
   ```

2. **Install Browsers**
   ```bash
   npm run install:browsers
   ```

3. **Run Tests**
   ```bash
   npm test
   ```

4. **View Reports**
   - Test Report: `test-report.md`
   - Defect Report: `defect-report.md`
   - HTML Report: `playwright-report/index.html`

## Test Coverage (40 Test Cases)

### ✅ Home Page (TC01-TC10)
- Page loading and service display
- Navigation to all services (Healthcare, Freelance, Car, Housekeeping, Finny)
- Navigation menu and authentication buttons
- Mobile responsiveness

### ✅ Authentication (TC11-TC20)  
- Login page loading and form validation
- Invalid credentials error handling
- Email format and required field validation
- Navigation to signup and forgot password
- Remember me and password visibility
- Enter key submission and mobile responsiveness

### ✅ Finny Money Management (TC21-TC30)
- Page loading and chat interface
- AI chat responses and transaction parsing
- Dashboard navigation and today's summary
- Category breakdown and manual transactions
- Chat mode, typing indicators, and multiple messages

### ✅ Healthcare Service (TC31-TC40)
- Page loading and doctor/patient navigation
- AI care access and doctor listing
- Specialization filtering and doctor search
- Appointment slots and booking process
- Availability filtering

## Key Features

🔍 **Comprehensive Coverage**: 40 test cases across all major modules
📊 **Automatic Reports**: Test report + MSBTE K Scheme defect report
📸 **Screenshot Capture**: All tests + defect highlighting
🌐 **Multi-Browser**: Chrome, Firefox, Safari, Mobile
🏗️ **Page Object Model**: Maintainable test architecture
⚡ **TypeScript**: Type-safe implementation

## Reports Generated

- `test-report.md` - Detailed test execution results
- `defect-report.md` - Professional defect reports (MSBTE format)
- `playwright-report/index.html` - Interactive HTML report
- `test-results/` - Screenshots, videos, traces

## Quick Commands

```bash
npm test                    # Run all tests
npm run test:headed         # Visible browser
npm run test:report         # With custom reporting
npm run test:debug          # Debug mode
```

**Test Engineer:ki Karunesh**  
**Total Test Cases: 40**  
**Coverage: Full E2E Audit**
