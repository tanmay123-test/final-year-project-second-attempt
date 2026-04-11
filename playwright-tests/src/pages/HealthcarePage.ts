import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class HealthcarePage extends BasePage {
  // Selectors
  private readonly doctorLoginButton = '[data-testid="doctor-login-btn"]';
  private readonly patientSignupButton = '[data-testid="patient-signup-btn"]';
  private readonly aiCareButton = '[data-testid="ai-care-btn"]';
  private readonly bookAppointmentButton = '[data-testid="book-appointment-btn"]';
  private readonly doctorDashboard = '[data-testid="doctor-dashboard"]';
  private readonly patientDashboard = '[data-testid="patient-dashboard"]';
  private readonly specializationFilter = '[data-testid="specialization-filter"]';
  private readonly doctorList = '[data-testid="doctor-list"]';
  private readonly appointmentForm = '[data-testid="appointment-form"]';
  private readonly availableSlots = '[data-testid="available-slots"]';

  constructor(page: Page) {
    super(page, '/healthcare');
  }

  async navigateToHealthcare(): Promise<void> {
    await this.navigate();
  }

  async isHealthcarePageLoaded(): Promise<boolean> {
    return await this.isVisible(this.doctorLoginButton) || 
           await this.isVisible(this.patientSignupButton);
  }

  async clickDoctorLogin(): Promise<void> {
    await this.clickElement(this.doctorLoginButton);
    await this.waitForNavigation();
  }

  async clickPatientSignup(): Promise<void> {
    await this.clickElement(this.patientSignupButton);
    await this.waitForNavigation();
  }

  async clickAiCare(): Promise<void> {
    await this.clickElement(this.aiCareButton);
    await this.waitForNavigation();
  }

  async clickBookAppointment(): Promise<void> {
    await this.clickElement(this.bookAppointmentButton);
  }

  async isDoctorDashboardVisible(): Promise<boolean> {
    return await this.isVisible(this.doctorDashboard);
  }

  async isPatientDashboardVisible(): Promise<boolean> {
    return await this.isVisible(this.patientDashboard);
  }

  async selectSpecialization(specialization: string): Promise<void> {
    await this.selectOption(this.specializationFilter, specialization);
    await this.page.waitForTimeout(2000); // Wait for filter to apply
  }

  async getDoctorCount(): Promise<number> {
    return await this.page.locator(this.doctorList).count();
  }

  async selectDoctor(doctorIndex: number): Promise<void> {
    const doctorCard = this.page.locator(`${this.doctorList} >> nth=${doctorIndex}`);
    await doctorCard.click();
  }

  async isAppointmentFormVisible(): Promise<boolean> {
    return await this.isVisible(this.appointmentForm);
  }

  async getAvailableSlotsCount(): Promise<number> {
    return await this.page.locator(this.availableSlots).count();
  }

  async selectTimeSlot(slotIndex: number): Promise<void> {
    const slot = this.page.locator(`${this.availableSlots} >> nth=${slotIndex}`);
    await slot.click();
  }

  async bookAppointment(appointmentData: {
    date: string;
    time: string;
    reason: string;
  }): Promise<void> {
    await this.fillInput('[data-testid="appointment-date"]', appointmentData.date);
    await this.fillInput('[data-testid="appointment-reason"]', appointmentData.reason);
    await this.selectTimeSlot(parseInt(appointmentData.time));
    await this.clickElement('[data-testid="confirm-appointment"]');
    await this.waitForNavigation();
  }

  async getAppointmentConfirmation(): Promise<string> {
    return await this.getText('[data-testid="appointment-confirmation"]');
  }

  async searchDoctor(doctorName: string): Promise<void> {
    await this.fillInput('[data-testid="doctor-search"]', doctorName);
    await this.page.waitForTimeout(2000);
  }

  async filterByAvailability(): Promise<void> {
    await this.clickElement('[data-testid="filter-available"]');
    await this.page.waitForTimeout(2000);
  }

  async getDoctorInfo(doctorIndex: number): Promise<{
    name: string;
    specialization: string;
    experience: string;
    rating: string;
  }> {
    const doctorCard = this.page.locator(`${this.doctorList} >> nth=${doctorIndex}`);
    return {
      name: await doctorCard.locator('[data-testid="doctor-name"]').textContent() || '',
      specialization: await doctorCard.locator('[data-testid="doctor-specialization"]').textContent() || '',
      experience: await doctorCard.locator('[data-testid="doctor-experience"]').textContent() || '',
      rating: await doctorCard.locator('[data-testid="doctor-rating"]').textContent() || ''
    };
  }
}
