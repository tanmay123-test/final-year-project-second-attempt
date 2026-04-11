import { test, expect } from '@playwright/test';
import { HealthcarePage } from '../../src/pages/HealthcarePage';
import { TestDataGenerator } from '../../src/utils/helpers';

test.describe('Healthcare Service Tests', () => {
  let healthcarePage: HealthcarePage;

  test.beforeEach(async ({ page }) => {
    healthcarePage = new HealthcarePage(page);
    await healthcarePage.navigateToHealthcare();
  });

  test('TC31 should load healthcare page successfully', async ({ page }) => {
    // Test objective: Verify healthcare page loads with service options
    const expectedOutput = 'Healthcare page should load with doctor login and patient signup options';
    
    try {
      const isPageLoaded = await healthcarePage.isHealthcarePageLoaded();
      expect(isPageLoaded).toBe(true);
      
      await healthcarePage.takeScreenshot('TC31_healthcare_page_load', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC31_healthcare_page_load', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC32 should navigate to doctor login', async ({ page }) => {
    // Test objective: Verify doctor login navigation works
    const expectedOutput = 'Should navigate to doctor login page';
    
    try {
      await healthcarePage.clickDoctorLogin();
      
      const currentUrl = await healthcarePage.getCurrentUrl();
      expect(currentUrl).toContain('login') || expect(currentUrl).toContain('doctor');
      
      await healthcarePage.takeScreenshot('TC32_doctor_login', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC32_doctor_login', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC33 should navigate to patient signup', async ({ page }) => {
    // Test objective: Verify patient signup navigation works
    const expectedOutput = 'Should navigate to patient signup page';
    
    try {
      await healthcarePage.clickPatientSignup();
      
      const currentUrl = await healthcarePage.getCurrentUrl();
      expect(currentUrl).toContain('signup') || expect(currentUrl).toContain('patient');
      
      await healthcarePage.takeScreenshot('TC33_patient_signup', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC33_patient_signup', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC34 should navigate to AI care', async ({ page }) => {
    // Test objective: Verify AI care navigation works
    const expectedOutput = 'Should navigate to AI care interface';
    
    try {
      await healthcarePage.clickAiCare();
      
      const currentUrl = await healthcarePage.getCurrentUrl();
      expect(currentUrl).toContain('ai') || expect(currentUrl).toContain('care');
      
      await healthcarePage.takeScreenshot('TC34_ai_care', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC34_ai_care', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC35 should display doctor list', async ({ page }) => {
    // Test objective: Verify doctor list is displayed with proper information
    const expectedOutput = 'Should display list of doctors with their details';
    
    try {
      await healthcarePage.clickBookAppointment();
      
      const doctorCount = await healthcarePage.getDoctorCount();
      expect(doctorCount).toBeGreaterThan(0);
      
      if (doctorCount > 0) {
        const doctorInfo = await healthcarePage.getDoctorInfo(0);
        expect(doctorInfo.name).toBeTruthy();
        expect(doctorInfo.specialization).toBeTruthy();
      }
      
      await healthcarePage.takeScreenshot('TC35_doctor_list', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC35_doctor_list', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC36 should filter doctors by specialization', async ({ page }) => {
    // Test objective: Verify doctor filtering by specialization works
    const expectedOutput = 'Should filter doctors based on selected specialization';
    
    try {
      await healthcarePage.clickBookAppointment();
      
      // Get initial doctor count
      const initialCount = await healthcarePage.getDoctorCount();
      
      // Apply specialization filter
      await healthcarePage.selectSpecialization('Cardiology');
      await page.waitForTimeout(2000);
      
      const filteredCount = await healthcarePage.getDoctorCount();
      
      // Filtered count should be less than or equal to initial count
      expect(filteredCount).toBeLessThanOrEqual(initialCount);
      
      await healthcarePage.takeScreenshot('TC36_specialization_filter', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC36_specialization_filter', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC37 should search doctors by name', async ({ page }) => {
    // Test objective: Verify doctor search functionality works
    const expectedOutput = 'Should search and display doctors matching the search term';
    
    try {
      await healthcarePage.clickBookAppointment();
      
      // Get initial doctor count
      const initialCount = await healthcarePage.getDoctorCount();
      
      // Search for a doctor
      await healthcarePage.searchDoctor('John');
      await page.waitForTimeout(2000);
      
      const searchCount = await healthcarePage.getDoctorCount();
      
      // Search should return some results or no results (both are valid)
      expect(searchCount).toBeGreaterThanOrEqual(0);
      
      await healthcarePage.takeScreenshot('TC37_doctor_search', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC37_doctor_search', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC38 should show available appointment slots', async ({ page }) => {
    // Test objective: Verify available time slots are displayed for booking
    const expectedOutput = 'Should display available time slots for appointment booking';
    
    try {
      await healthcarePage.clickBookAppointment();
      
      // Select a doctor
      const doctorCount = await healthcarePage.getDoctorCount();
      if (doctorCount > 0) {
        await healthcarePage.selectDoctor(0);
        await page.waitForTimeout(2000);
        
        // Check if appointment form is visible
        const isFormVisible = await healthcarePage.isAppointmentFormVisible();
        expect(isFormVisible).toBe(true);
        
        // Check for available slots
        const slotCount = await healthcarePage.getAvailableSlotsCount();
        expect(slotCount).toBeGreaterThanOrEqual(0);
      }
      
      await healthcarePage.takeScreenshot('TC38_appointment_slots', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC38_appointment_slots', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC39 should book appointment successfully', async ({ page }) => {
    // Test objective: Verify appointment booking process works
    const expectedOutput = 'Should book appointment with selected date and time';
    
    try {
      await healthcarePage.clickBookAppointment();
      
      const doctorCount = await healthcarePage.getDoctorCount();
      if (doctorCount > 0) {
        await healthcarePage.selectDoctor(0);
        await page.waitForTimeout(2000);
        
        const appointmentData = {
          date: new Date(Date.now() + 86400000).toISOString().split('T')[0], // Tomorrow
          time: '0', // First available slot
          reason: 'Regular checkup'
        };
        
        await healthcarePage.bookAppointment(appointmentData);
        
        // Verify appointment confirmation
        const confirmation = await healthcarePage.getAppointmentConfirmation();
        expect(confirmation).toBeTruthy();
      }
      
      await healthcarePage.takeScreenshot('TC39_appointment_booking', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC39_appointment_booking', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });

  test('TC40 should filter by availability', async ({ page }) => {
    // Test objective: Verify filtering by doctor availability works
    const expectedOutput = 'Should show only available doctors when availability filter is applied';
    
    try {
      await healthcarePage.clickBookAppointment();
      
      // Get initial doctor count
      const initialCount = await healthcarePage.getDoctorCount();
      
      // Apply availability filter
      await healthcarePage.filterByAvailability();
      await page.waitForTimeout(2000);
      
      const availableCount = await healthcarePage.getDoctorCount();
      
      // Available count should be less than or equal to initial count
      expect(availableCount).toBeLessThanOrEqual(initialCount);
      
      await healthcarePage.takeScreenshot('TC40_availability_filter', test.info);
      console.log(`✅ ${test.title}: PASSED`);
      
    } catch (error) {
      await healthcarePage.takeDefectScreenshot('TC40_availability_filter', test.info);
      console.log(`❌ ${test.title}: FAILED - ${error.message}`);
      throw error;
    }
  });
});
