import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DoctorProfile = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [consultationFee, setConsultationFee] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const token = localStorage.getItem('doctorToken');
            if (!token) {
                setError('No authentication token found');
                setLoading(false);
                return;
            }

            const response = await axios.get('/api/doctor/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.data) {
                setProfile(response.data);
                setConsultationFee(response.data.consultation_fee || '');
            }
        } catch (error) {
            setError(error.response?.data?.error || 'Failed to fetch profile');
        } finally {
            setLoading(false);
        }
    };

    const handleFeeUpdate = async (e) => {
        e.preventDefault();
        
        if (!consultationFee || consultationFee < 0) {
            setError('Please enter a valid consultation fee');
            return;
        }

        setSaving(true);
        setError('');
        setMessage('');

        try {
            const token = localStorage.getItem('doctorToken');
            const response = await axios.put('/api/doctor/update-fee', 
                { consultation_fee: parseInt(consultationFee) },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.success) {
                setMessage('Consultation fee updated successfully!');
                // Update local profile
                if (profile) {
                    setProfile({
                        ...profile,
                        consultation_fee: response.data.consultation_fee
                    });
                }
            }
        } catch (error) {
            setError(error.response?.data?.error || 'Failed to update consultation fee');
        } finally {
            setSaving(false);
        }
    };

    const calculatePlatformFee = () => {
        const fee = parseInt(consultationFee) || 0;
        const platformFee = Math.round(fee * 0.20);
        const total = fee + platformFee;
        return { platformFee, total };
    };

    if (loading) {
        return (
            <div className="container mt-4">
                <div className="text-center">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-2">Loading profile...</p>
                </div>
            </div>
        );
    }

    const { platformFee, total } = calculatePlatformFee();

    return (
        <div className="container mt-4">
            <div className="row justify-content-center">
                <div className="col-md-8">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="mb-0">Doctor Profile</h4>
                        </div>
                        <div className="card-body">
                            {profile && (
                                <div className="mb-4">
                                    <h5>Personal Information</h5>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <p><strong>Name:</strong> {profile.doctor_name}</p>
                                            <p><strong>Email:</strong> {profile.email}</p>
                                            <p><strong>Phone:</strong> {profile.phone}</p>
                                        </div>
                                        <div className="col-md-6">
                                            <p><strong>Specialization:</strong> {profile.specialization}</p>
                                            <p><strong>Experience:</strong> {profile.experience} years</p>
                                            <p><strong>Rating:</strong> ⭐ {profile.rating || 'Not rated'}</p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div className="border-top pt-4">
                                <h5>Consultation Fee Settings</h5>
                                <form onSubmit={handleFeeUpdate}>
                                    <div className="mb-3">
                                        <label htmlFor="consultationFee" className="form-label">
                                            Clinic Consultation Fee (₹)
                                        </label>
                                        <div className="input-group">
                                            <span className="input-group-text">₹</span>
                                            <input
                                                type="number"
                                                className="form-control"
                                                id="consultationFee"
                                                value={consultationFee}
                                                onChange={(e) => setConsultationFee(e.target.value)}
                                                placeholder="Enter your consultation fee"
                                                min="0"
                                                step="50"
                                                required
                                            />
                                        </div>
                                        <div className="form-text text-muted">
                                            Platform automatically adds service charges on top of this fee.
                                        </div>
                                    </div>

                                    {consultationFee && (
                                        <div className="alert alert-info mb-3">
                                            <h6>Price Breakdown:</h6>
                                            <div className="d-flex justify-content-between">
                                                <span>Your Fee:</span>
                                                <span>₹{consultationFee}</span>
                                            </div>
                                            <div className="d-flex justify-content-between">
                                                <span>Platform Fee (20%):</span>
                                                <span>₹{platformFee}</span>
                                            </div>
                                            <hr />
                                            <div className="d-flex justify-content-between fw-bold">
                                                <span>Patient Pays:</span>
                                                <span>₹{total}</span>
                                            </div>
                                        </div>
                                    )}

                                    {error && (
                                        <div className="alert alert-danger">
                                            {error}
                                        </div>
                                    )}

                                    {message && (
                                        <div className="alert alert-success">
                                            {message}
                                        </div>
                                    )}

                                    <button
                                        type="submit"
                                        className="btn btn-primary"
                                        disabled={saving}
                                    >
                                        {saving ? (
                                            <>
                                                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                                Saving...
                                            </>
                                        ) : (
                                            'Update Consultation Fee'
                                        )}
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DoctorProfile;
