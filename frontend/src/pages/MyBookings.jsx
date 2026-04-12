import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../shared/api';
import healthcareSocket from '../services/healthcareSocket';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all'); // 'all' | 'active' | 'completed' | 'cancelled'
  const { user } = useAuth();

  useEffect(() => {
    fetchAllBookings();
    
    // Initialize Healthcare Socket for real-time updates
    if (user?.user_id) {
      healthcareSocket.connect();
      healthcareSocket.joinRoom('user', user.user_id);

      const handleUpdate = (data) => {
        console.log('🔄 Real-time booking update:', data);
        fetchAllBookings(); // Refresh all
        
        if (Notification.permission === "granted") {
          new Notification("Booking Update", {
            body: `Your booking status has been updated to ${data.status}`
          });
        }
      };

      healthcareSocket.on('appointment_update', handleUpdate);

      return () => {
        healthcareSocket.off('appointment_update', handleUpdate);
        healthcareSocket.leaveRoom('user', user.user_id);
      };
    }
  }, [user]);

  const fetchAllBookings = async () => {
    try {
      setLoading(true);
      const [mechanicRes, towRes, fuelRes] = await Promise.allSettled([
        api.getUserAppointments().catch(err => ({ data: { success: false, appointments: [] } })),
        api.getUserTowBookings().catch(err => ({ data: { success: false, bookings: [] } })),
        api.getUserFuelDeliveryBookings().catch(err => ({ data: { success: false, bookings: [] } }))
      ]);

      const allBookings = [];
      
      if (mechanicRes.status === 'fulfilled' && mechanicRes.value?.data?.success) {
        mechanicRes.value.data.appointments.forEach(apt => {
          allBookings.push({
            ...apt,
            service_type: 'mechanic',
            display_name: apt.doctor_name || apt.worker_name || 'Expert Mechanic',
            display_role: 'Mechanic Specialist',
            display_status: apt.status || 'pending',
            vehicle: apt.car_name || 'Vehicle',
            license: apt.license_plate || 'PR-911-S',
            details: apt.issue_description || 'General maintenance',
            date: apt.appointment_date || apt.created_at,
            time: apt.appointment_time || '09:30 AM',
            job_id: `#EXP-${apt.id}-XP`,
            image: apt.worker_image || 'https://lh3.googleusercontent.com/aida-public/AB6AXuB4di-NTf3OKwxTvxZm4mgYZG8Dn_verOfimHS_JGZK7FzHsXlqSRtJ9_gt2gBTon_U5qyIXG0nVPgsGCG-4yOMSUhxC51UM3rotcBAH0R94h-KOrK6rjJuSgCUfVydQu0yQzJd59MjLOcFklou6mbXB9QhKax1ZtoZCMiJUEK7poh8OIeEMoFCr-Jf_Bv_KYltuI8eKVaPr-GUkzK4-NwVXMdst1YHyTRJN3lzfd6DWnzDtUB3sjTQ8v3lFtQmDMbZpvr31xsfDut8'
          });
        });
      }

      if (towRes.status === 'fulfilled' && towRes.value?.data?.success) {
        towRes.value.data.bookings.forEach(booking => {
          allBookings.push({
            ...booking,
            service_type: 'tow',
            display_name: booking.worker_name || booking.driver_name || 'Tow Operator',
            display_role: 'Towing Expert',
            display_status: booking.status || 'pending',
            vehicle: booking.car_name || 'Vehicle',
            license: booking.license_plate || 'TW-882-C',
            details: `Tow from ${booking.pickup_address || 'Current Location'}`,
            date: booking.created_at || booking.booking_date,
            time: 'ASAP',
            job_id: `#EXP-${booking.id}-TW`,
            image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBHdnc_q9ZEM31T0UwWgnFhTTr2G6qwO47zcjNTVE-V-vohDyx-MVwl7NV24NmrkaYBMN3Wh7KAwd49F_HEeEoYCwoh9q2HMV2Wel--3sf2ds-hzW2yVKOcIPjhKVBUP544QHRN-kmNlboUM726QFWEH4JjGMiAWfk88ZuCPU7T7WF109T7OTpVnJkl8Nohmld7hHUm40U-U7UAZjg3MPWDdrCs4RBmdpzG4LXQnCTyFKk8RXScHWrLWDpqGUVp1sv0Knm1kkF0F7yv'
          });
        });
      }

      if (fuelRes.status === 'fulfilled' && fuelRes.value?.data?.success) {
        fuelRes.value.data.bookings.forEach(booking => {
          allBookings.push({
            ...booking,
            service_type: 'fuel',
            display_name: booking.worker_name || booking.station_name || 'Fuel Station',
            display_role: 'Fuel Specialist',
            display_status: booking.status || 'pending',
            vehicle: booking.car_name || 'Vehicle',
            license: booking.license_plate || 'FL-ROT-95',
            details: `${booking.quantity_liters || booking.quantity || 0}L of ${booking.fuel_type || 'Fuel'}`,
            date: booking.created_at || booking.booking_date,
            time: 'Instant',
            job_id: `#EXP-${booking.id}-FL`,
            image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDR8EMHCPlmfnoM_tSlwSPLIooqEJe2h3GTurI-HKO-INuvA1hf3mK-K_XhQ1ceJOI4KBhCJfnNpxfVN9y-9Wqf_eOgjYLQfGpRQmZ1J13g5FNwA-ik0aOLrE6V5oL-G8kb0L6pvubTN2sLdASZg-urtU4y-SG9subhcG_BjldGADG1yyU05MaGrmDmvxw0JlZdgul_qMmPz5i5lfG1zDluEAe0mb2rwaAFRJMa4RZxdIi8I-ZlnbSugQ-CvLTiDnxjdKxDjvFddGP7'
          });
        });
      }

      allBookings.sort((a, b) => new Date(b.date) - new Date(a.date));
      setBookings(allBookings);
    } catch (err) {
      console.error('Failed to fetch bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredBookings = useMemo(() => {
    if (filterStatus === 'all') return bookings;
    if (filterStatus === 'active') {
      return bookings.filter(b => ['pending', 'searching', 'accepted', 'in_progress'].includes(b.display_status.toLowerCase()));
    }
    return bookings.filter(b => b.display_status.toLowerCase() === filterStatus.toLowerCase());
  }, [bookings, filterStatus]);

  const getStatusStyle = (status) => {
    const s = status.toLowerCase();
    if (s === 'searching' || s === 'pending') return 'bg-secondary-container/15 text-secondary';
    if (s === 'accepted' || s === 'in_progress') return 'bg-primary/10 text-primary';
    if (s === 'completed') return 'bg-tertiary-container/10 text-tertiary';
    if (s === 'cancelled') return 'bg-error-container/40 text-error';
    return 'bg-surface-container-high text-on-surface-variant';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Oct 24, 2023';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 pt-12 pb-32">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-12">
        <div>
          <h1 className="font-headline font-extrabold text-5xl tracking-tight text-on-surface mb-4">My Bookings</h1>
          <p className="text-on-surface-variant max-w-md font-body leading-relaxed">
            Track and manage your service appointments. Precision maintenance for your high-performance vehicle.
          </p>
        </div>
        <div className="flex flex-wrap items-center bg-surface-container-low p-1.5 rounded-xl">
          {['all', 'active', 'completed', 'cancelled'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                filterStatus === status 
                  ? 'bg-surface-container-lowest text-primary shadow-sm' 
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filteredBookings.length === 0 ? (
        <div className="text-center py-20 bg-surface-container-lowest rounded-2xl border border-outline-variant/15">
          <span className="material-symbols-outlined text-6xl text-outline-variant mb-4">calendar_today</span>
          <h3 className="text-xl font-bold text-on-surface">No bookings found</h3>
          <p className="text-on-surface-variant">You don't have any {filterStatus !== 'all' ? filterStatus : ''} bookings yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {filteredBookings.map((booking) => (
            <div key={booking.job_id} className="group bg-surface-container-lowest p-6 rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] hover:bg-surface-bright transition-all border border-outline-variant/15">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl overflow-hidden shadow-inner">
                    <img 
                      className="w-full h-full object-cover" 
                      src={booking.image} 
                      alt={booking.display_name} 
                    />
                  </div>
                  <div>
                    <h3 className="font-headline font-bold text-lg text-on-surface">{booking.display_name}</h3>
                    <p className="text-xs font-label uppercase tracking-widest text-on-surface-variant">{booking.display_role}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-[4px] text-[10px] font-label font-bold tracking-wider uppercase ${getStatusStyle(booking.display_status)}`}>
                  {booking.display_status}
                </span>
              </div>

              <div className="space-y-4 mb-8">
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary text-xl">car_repair</span>
                  <div>
                    <p className="text-sm font-semibold text-on-surface">{booking.vehicle}</p>
                    <p className="text-xs text-on-surface-variant">License: {booking.license}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary text-xl">build</span>
                  <p className="text-sm text-on-surface-variant line-clamp-1 leading-relaxed">{booking.details}</p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary text-xl">schedule</span>
                  <p className="text-sm text-on-surface-variant">{formatDate(booking.date)} • {booking.time}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-outline-variant/10">
                <span className="text-[10px] font-label font-medium text-outline">JOB ID: {booking.job_id}</span>
                <button className="px-5 py-2 text-sm font-bold text-primary hover:bg-primary/5 rounded-lg transition-all">View Details</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyBookings;
