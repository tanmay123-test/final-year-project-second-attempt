/**
 * Healthcare Service using Organized Database API
 * Replaces the old scattered database approach
 */

import { healthcareAPI, userAuthAPI, apiUtils } from '../../organizedApi.js';

console.log('[CLI] Healthcare service initialized (using organized database)');

// Get specializations
export const getSpecializations = async () => {
  console.log('[CLI] Fetching specializations from organized database...');
  
  try {
    const response = await healthcareAPI.getSpecializations();
    console.log('[CLI] Specializations fetched:', response.data.length, 'items');
    return response.data;
  } catch (error) {
    console.error('[CLI] Error fetching specializations:', error);
    
    // Return mock data for development
    console.log('[CLI] Using mock specializations data');
    return [
      { id: 1, name: 'General', icon: 'stethoscope' },
      { id: 2, name: 'Cardiology', icon: 'heart' },
      { id: 3, name: 'Dermatology', icon: 'skin' },
      { id: 4, name: 'Pediatrics', icon: 'baby' },
      { id: 5, name: 'Orthopedics', icon: 'bone' }
    ];
  }
};

// Get top doctors using organized database
export const getTopDoctors = async () => {
  console.log('[CLI] Fetching top doctors from organized database...');
  
  try {
    const response = await healthcareAPI.getDoctors({ is_verified: true, limit: 10 });
    console.log('[CLI] Top doctors fetched:', response.data.workers.length, 'items');
    
    // Transform data to match expected format
    return response.data.workers.map(worker => ({
      id: worker.id,
      name: worker.name,
      specialization: worker.worker_type || 'General Practitioner',
      rating: 4.5 + Math.random() * 0.5, // Mock rating for now
      experience: Math.floor(Math.random() * 20) + 5, // Mock experience
      hospital: 'City Hospital', // Mock hospital
      price: Math.floor(Math.random() * 500) + 200, // Mock price
      phone: worker.phone,
      email: worker.email,
      is_verified: worker.is_verified
    }));
  } catch (error) {
    console.error('[CLI] Error fetching top doctors:', error);
    
    // Return mock data for development
    console.log('[CLI] Using mock doctors data');
    return [
      {
        id: 1,
        name: 'Dr. Sarah Johnson',
        specialization: 'Cardiologist',
        rating: 4.9,
        experience: 12,
        hospital: 'Apollo Hospital, Delhi',
        price: 500,
        phone: '+91-9876543210',
        email: 'sarah.johnson@apollo.com',
        is_verified: true
      },
      {
        id: 2,
        name: 'Dr. Michael Chen',
        specialization: 'Dermatologist',
        rating: 4.8,
        experience: 8,
        hospital: 'Fortis Healthcare, Mumbai',
        price: 600,
        phone: '+91-9876543211',
        email: 'michael.chen@fortis.com',
        is_verified: true
      },
      {
        id: 3,
        name: 'Dr. Emily Rodriguez',
        specialization: 'Pediatrician',
        rating: 4.9,
        experience: 15,
        hospital: 'AIIMS, Delhi',
        price: 450,
        phone: '+91-9876543212',
        email: 'emily.rodriguez@aiims.com',
        is_verified: true
      }
    ];
  }
};

// Book appointment using organized database
export const bookAppointment = async (doctorId, appointmentData) => {
  console.log('[CLI] Booking appointment for doctor:', doctorId);
  
  try {
    const bookingData = {
      worker_id: doctorId,
      user_id: apiUtils.getCurrentUser()?.id,
      service_type: 'healthcare',
      booking_data: {
        ...appointmentData,
        appointment_type: 'consultation',
        status: 'pending'
      }
    };
    
    const response = await healthcareAPI.createAppointment(bookingData);
    console.log('[CLI] Appointment booked successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('[CLI] Error booking appointment:', error);
    throw error;
  }
};

// Get user appointments
export const getUserAppointments = async () => {
  console.log('[CLI] Fetching user appointments from organized database...');
  
  try {
    const user = apiUtils.getCurrentUser();
    if (!user) {
      throw new Error('User not authenticated');
    }
    
    const response = await healthcareAPI.getAppointments({ user_id: user.id });
    console.log('[CLI] User appointments fetched:', response.data.length, 'items');
    return response.data;
  } catch (error) {
    console.error('[CLI] Error fetching user appointments:', error);
    return [];
  }
};

// Get doctor availability
export const getDoctorAvailability = async (doctorId) => {
  console.log('[CLI] Fetching doctor availability from organized database...');
  
  try {
    // This would be implemented as a separate endpoint
    // For now, return mock availability
    return {
      available_slots: [
        '2024-03-20T09:00:00',
        '2024-03-20T10:00:00',
        '2024-03-20T11:00:00',
        '2024-03-20T14:00:00',
        '2024-03-20T15:00:00'
      ]
    };
  } catch (error) {
    console.error('[CLI] Error fetching doctor availability:', error);
    return { available_slots: [] };
  }
};

// Cancel appointment
export const cancelAppointment = async (appointmentId) => {
  console.log('[CLI] Cancelling appointment:', appointmentId);
  
  try {
    const response = await healthcareAPI.updateAppointment(appointmentId, { status: 'cancelled' });
    console.log('[CLI] Appointment cancelled successfully');
    return response.data;
  } catch (error) {
    console.error('[CLI] Error cancelling appointment:', error);
    throw error;
  }
};

// Rate doctor/service
export const rateService = async (bookingId, rating, review) => {
  console.log('[CLI] Rating service:', bookingId, rating);
  
  try {
    const response = await api.post(`/api/reviews/healthcare/${bookingId}`, {
      rating,
      review_text: review
    });
    console.log('[CLI] Service rated successfully');
    return response.data;
  } catch (error) {
    console.error('[CLI] Error rating service:', error);
    throw error;
  }
};

// Get doctor by specialization
export const getDoctorsBySpecialization = async (specialization) => {
  console.log('[CLI] Fetching doctors by specialization:', specialization);
  
  try {
    const response = await healthcareAPI.getDoctors({ 
      specialization: specialization,
      is_verified: true 
    });
    
    return response.data.workers.map(worker => ({
      id: worker.id,
      name: worker.name,
      specialization: specialization,
      rating: 4.5 + Math.random() * 0.5,
      experience: Math.floor(Math.random() * 20) + 5,
      hospital: 'City Hospital',
      price: Math.floor(Math.random() * 500) + 200,
      phone: worker.phone,
      email: worker.email,
      is_verified: worker.is_verified
    }));
  } catch (error) {
    console.error('[CLI] Error fetching doctors by specialization:', error);
    return [];
  }
};

// Search doctors
export const searchDoctors = async (query) => {
  console.log('[CLI] Searching doctors:', query);
  
  try {
    const response = await healthcareAPI.getDoctors({ 
      search: query,
      is_verified: true 
    });
    
    return response.data.workers.map(worker => ({
      id: worker.id,
      name: worker.name,
      specialization: worker.worker_type || 'General Practitioner',
      rating: 4.5 + Math.random() * 0.5,
      experience: Math.floor(Math.random() * 20) + 5,
      hospital: 'City Hospital',
      price: Math.floor(Math.random() * 500) + 200,
      phone: worker.phone,
      email: worker.email,
      is_verified: worker.is_verified
    }));
  } catch (error) {
    console.error('[CLI] Error searching doctors:', error);
    return [];
  }
};

// Get healthcare statistics
export const getHealthcareStatistics = async () => {
  console.log('[CLI] Fetching healthcare statistics...');
  
  try {
    const response = await api.get('/api/statistics/healthcare');
    console.log('[CLI] Healthcare statistics fetched');
    return response.data.statistics;
  } catch (error) {
    console.error('[CLI] Error fetching healthcare statistics:', error);
    return null;
  }
};
